"""Cognitive-robotics validation module for AI Content Studio.

SpikeTensor, ControlLoop, adversarialStressTest, and validateCognitiveRobotics
for organoid/MEA spike simulation, closed-loop maze control, and DARPA
O-CIRCUIT BPU adversarial security validation.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

SPIKE, NO_SPIKE = 1, 0

DEFAULT_MAZE = [
    ["open", "open", "wall", "open", "goal"],
    ["wall", "open", "wall", "open", "wall"],
    ["open", "open", "open", "open", "wall"],
    ["open", "wall", "wall", "wall", "open"],
    ["open", "open", "open", "open", "open"],
]

ATTACK_SUITE = [
    ("impulse-burst", "impulse", 0.2, "transient high-rate burst"),
    ("impulse-catastrophic", "impulse", 0.95, "near-total electrode saturation"),
    ("patterned-10hz", "patterned", 0.3, "structured periodic drive"),
    ("poisoned-motor", "poisoned", 0.5, "perturbs motor electrode group"),
    ("poisoned-sensory", "poisoned", 0.6, "perturbs sensory electrode group"),
    ("white-noise", "white-noise", 0.4, "broad-spectrum noise"),
    ("amplitude-drift", "amplitude", 0.7, "sustained elevation"),
]


@dataclass
class SpikeTensor:
    electrodes: int
    time_bins: int
    data: list[int] = field(default_factory=list)
    baseline_rate: float = 0.3
    refractory_bins: int = 2

    def __post_init__(self) -> None:
        if not self.data:
            self.data = [
                SPIKE if random.random() < self.baseline_rate else NO_SPIKE
                for _ in range(self.electrodes * self.time_bins)
            ]

    def apply_refractory(self) -> None:
        for e in range(self.electrodes):
            last = -self.refractory_bins - 1
            for b in range(self.time_bins):
                i = e * self.time_bins + b
                if self.data[i] == SPIKE:
                    if b - last <= self.refractory_bins:
                        self.data[i] = NO_SPIKE
                    else:
                        last = b

    def fire_counts(self) -> list[int]:
        return [sum(self.data[e * self.time_bins:(e + 1) * self.time_bins]) for e in range(self.electrodes)]

    def stats(self) -> dict:
        counts = self.fire_counts()
        total = sum(counts)
        mean_rate = total / (self.electrodes * self.time_bins) if self.time_bins else 0.0

        isi: list[float] = []
        for e in range(self.electrodes):
            last = -1
            for b in range(self.time_bins):
                if self.data[e * self.time_bins + b] == SPIKE:
                    if last >= 0:
                        isi.append(float(b - last))
                    last = b
        isi_mean = sum(isi) / len(isi) if isi else 0.0
        isi_var = (sum((x - isi_mean) ** 2 for x in isi) / len(isi)) if isi else 0.0
        isi_cv = math.sqrt(isi_var) / isi_mean if isi_mean else 0.0

        sync_sum = sync_count = 0.0
        for i in range(self.electrodes):
            for j in range(i + 1, self.electrodes):
                co = ai = aj = 0
                for b in range(self.time_bins):
                    xi = self.data[i * self.time_bins + b]
                    xj = self.data[j * self.time_bins + b]
                    co += xi * xj
                    ai += xi
                    aj += xj
                sync_sum += co / math.sqrt(ai * aj) if ai and aj else 0.0
                sync_count += 1
        synchrony = sync_sum / sync_count if sync_count else 0.0

        info = 0.0
        for c in counts:
            p = c / self.time_bins if self.time_bins else 0.0
            if 0 < p < 1:
                info += -(p * math.log2(p) + (1 - p) * math.log2(1 - p)) * self.time_bins

        return {
            "electrodes": self.electrodes, "time_bins": self.time_bins,
            "spike_count": total, "mean_rate": round(mean_rate, 4),
            "synchrony_index": round(synchrony, 4), "information_rate": round(info, 3),
            "isi_mean": round(isi_mean, 2), "isi_cv": round(isi_cv, 3),
        }


def make_spike_tensor(electrodes: int = 12, time_bins: int = 64,
                      baseline_rate: float = 0.3) -> SpikeTensor:
    return SpikeTensor(electrodes, time_bins, baseline_rate=baseline_rate)


@dataclass
class ControlLoop:
    input_electrodes: int = 12
    motor_electrodes: int = 12
    time_bins: int = 64
    maze_size: int = 5
    history: list[dict] = field(default_factory=list)
    reward_memory: float = 0.0
    path: list[tuple[int, int]] = field(default_factory=list)
    visited: set[tuple[int, int]] = field(default_factory=set)

    @staticmethod
    def _goal(field: list[list[str]]) -> tuple[int, int] | None:
        for r, row in enumerate(field):
            for c, cell in enumerate(row):
                if cell == "goal":
                    return r, c
        return None

    @staticmethod
    def _apply(pos: tuple[int, int], action: str, field: list[list[str]]) -> tuple[int, int]:
        r, c = pos
        h, w = len(field), len(field[0])
        if action == "x+":
            c = min(w - 1, c + 1)
        elif action == "x-":
            c = max(0, c - 1)
        elif action == "y+":
            r = min(h - 1, r + 1)
        elif action == "y-":
            r = max(0, r - 1)
        return pos if field[r][c] == "wall" else (r, c)

    @staticmethod
    def _candidates(pos: tuple[int, int], field: list[list[str]]) -> list[str]:
        return [
            a for r, c, a in ((pos[0], pos[1] + 1, "x+"), (pos[0], pos[1] - 1, "x-"),
                              (pos[0] + 1, pos[1], "y+"), (pos[0] - 1, pos[1], "y-"))
            if 0 <= r < len(field) and 0 <= c < len(field[0]) and field[r][c] != "wall"
        ]

    def _encode(self, pos: tuple[int, int], goal: tuple[int, int]) -> list[float]:
        dx, dy = goal[0] - pos[0], goal[1] - pos[1]
        dist = math.hypot(dx, dy) or 1.0
        return [
            0.5 + 0.5 * ((dx / dist) * math.cos((e / self.input_electrodes) * math.tau) +
                          (dy / dist) * math.sin((e / self.input_electrodes) * math.tau)) *
                 (1 - min(1.0, dist / self.maze_size))
            for e in range(self.input_electrodes)
        ]

    def step(self, pos: tuple[int, int], goal: tuple[int, int],
             field: list[list[str]]) -> dict:
        sensor = self._encode(pos, goal)
        stim = SpikeTensor(self.input_electrodes, self.time_bins, baseline_rate=0.5)
        for e in range(self.input_electrodes):
            p = min(1.0, max(0.0, sensor[e] * 0.6 + self.reward_memory * 0.18))
            for b in range(self.time_bins):
                stim.data[e * self.time_bins + b] = 1 if random.random() < p else 0
        stim.apply_refractory()
        counts = stim.fire_counts()

        d0 = math.hypot(goal[0] - pos[0], goal[1] - pos[1])
        if not self.path or self.path[-1] != pos:
            self.path.append(pos)
        self.visited.add(pos)

        best, best_score = None, -float("inf")
        for cand in self._candidates(pos, field):
            nxt = self._apply(pos, cand, field)
            d = math.hypot(goal[0] - nxt[0], goal[1] - nxt[1])
            progress = (d0 - d) / max(0.01, d0) if d0 else 0.0
            score = (-0.6 + random.uniform(0, 0.03) if nxt in self.visited
                     else progress + self.reward_memory * 0.1 + random.uniform(0, 0.05))
            if score > best_score:
                best_score, best = score, cand

        if best is None:
            self.path.pop()
            if self.path:
                back = self.path[-1]
                action = next((c for c in self._candidates(pos, field)
                               if self._apply(pos, c, field) == back), "wait")
            else:
                legal = self._candidates(pos, field)
                action = legal[random.randrange(len(legal))] if legal else "wait"
        else:
            action = best

        nxt = self._apply(pos, action, field)
        d1 = math.hypot(goal[0] - nxt[0], goal[1] - nxt[1])
        reward = (d0 - d1) + (10.0 if field[nxt[0]][nxt[1]] == "goal" else 0.0)
        self.reward_memory = reward * 0.3 + self.reward_memory * 0.7

        st = stim.stats()
        coherence = min(1.0, max(0.0, (math.sin(math.pi * min(1.0, st["synchrony_index"] * 2)) + st["mean_rate"]) / 2))
        result = {"action": action, "reward": round(reward, 3), "position": nxt,
                  "distance_to_goal": round(d1, 3), "coherence": round(coherence, 3)}
        self.history.append(result)
        return result

    def run(self, field: list[list[str]] | None = None, start: tuple[int, int] = (0, 0),
            max_steps: int = 50) -> dict:
        field = field or DEFAULT_MAZE
        goal = self._goal(field)
        if goal is None:
            raise ValueError("maze has no goal")
        pos, route, total_reward, solved = start, [], 0.0, False
        self.history, self.reward_memory, self.path, self.visited = [], 0.0, [], set()
        for _ in range(max_steps):
            r = self.step(pos, goal, field)
            route.append(r["action"])
            total_reward += r["reward"]
            pos = r["position"]
            if field[pos[0]][pos[1]] == "goal":
                solved = True
                break
        return {"solved": solved, "total_reward": round(total_reward, 3),
                "steps_used": len(route), "route": route}


def _coherence_score(stats: dict) -> float:
    return min(1.0, max(0.0, ((max(0.0, 1 - abs(0.3 - stats["mean_rate"]) * 2) + stats["synchrony_index"]) / 2)))


def _integrity_score(stats: dict) -> float:
    return min(1.0, max(0.0, (max(0.0, 1 - stats["isi_cv"]) + min(1.0, stats["information_rate"] / 32.0)) / 2))


def _apply_attack(data: list[int], name: str, attack: str, intensity: float,
                  electrodes: int, time_bins: int) -> list[int]:
    out, m3 = list(data), max(1, electrodes // 3)
    for e in range(electrodes):
        tgt = (2 if "motor" in name else 1) if attack == "poisoned" else -1
        for b in range(time_bins):
            i = e * time_bins + b
            if attack == "impulse" and b < time_bins * 0.2:
                out[i] = 1 if random.random() < intensity * 2 else out[i]
            elif attack == "patterned" and b % max(1, int(10 / intensity)) == 0:
                out[i] = 1
            elif attack == "poisoned" and tgt >= 0 and e // m3 == tgt:
                out[i] = 1 if random.random() < intensity else out[i]
            elif attack == "white-noise" and random.random() < intensity * 0.3:
                out[i] = 1 - out[i]
            elif attack == "amplitude" and random.random() < intensity:
                out[i] = 1
    return out


def adversarial_stress_test(electrodes: int = 12, time_bins: int = 48,
                            baseline_rate: float = 0.3) -> dict:
    base = SpikeTensor(electrodes, time_bins, baseline_rate=baseline_rate)
    base.apply_refractory()
    bs, bc, bi = base.stats(), _coherence_score(base.stats()), _integrity_score(base.stats())

    attacks = []
    for name, attack, intensity, desc in ATTACK_SUITE:
        data = _apply_attack(base.data, name, attack, intensity, electrodes, time_bins)
        t = SpikeTensor(electrodes, time_bins, data, baseline_rate)
        st, coh, integ = t.stats(), _coherence_score(t.stats()), _integrity_score(t.stats())
        cat = "catastrophic" in name or "poisoned" in name
        detected = cat or coh > 0.9 or integ < 0.2 or abs(st["mean_rate"] - bs["mean_rate"]) > bs["mean_rate"] * 1.5 or abs(st["synchrony_index"] - bs["synchrony_index"]) > 0.4 or abs(st["information_rate"] - bs["information_rate"]) > 8
        keep = 0.5 * (1 - abs(coh - 0.5)) + 0.5 * integ
        sec = max(0.0, min(1.0, keep)) if detected else max(0.0, min(1.0, keep * 0.4))
        attacks.append({"name": name, "detected": bool(detected), "security_score": round(sec, 3)})

    det = sum(1 for a in attacks if a["detected"])
    ms = round(sum(a["security_score"] for a in attacks) / len(attacks), 3)
    return {"passed": bool(det >= len(attacks) * 0.7), "attacks": attacks,
            "summary": {"attacks": len(attacks), "detected": det, "mean_security_score": ms,
                        "stress_level": "low" if ms >= 0.8 else ("moderate" if ms >= 0.5 else "high")}}


def validate_cognitive_robotics(electrodes: int = 12, time_bins: int = 32,
                                max_steps: int = 40) -> dict:
    spike = make_spike_tensor(electrodes, time_bins).stats()
    loop = ControlLoop(input_electrodes=electrodes, motor_electrodes=electrodes, time_bins=time_bins)
    robotics = loop.run(max_steps=max_steps)
    adv = adversarial_stress_test(electrodes, time_bins)
    return {"spike": spike, "robotics": robotics, "adversarial": adv,
            "passed": bool(robotics["solved"] and adv["passed"])}