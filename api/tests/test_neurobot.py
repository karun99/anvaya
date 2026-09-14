"""Tests for the cognitive-robotics validation module."""

import unittest
from neurobot import (SpikeTensor, make_spike_tensor, ControlLoop, DEFAULT_MAZE,
                      adversarial_stress_test, validate_cognitive_robotics, ATTACK_SUITE)


class TestSpikeTensor(unittest.TestCase):
    def test_stats_bounds(self):
        s = make_spike_tensor(8, 64, 0.3).stats()
        self.assertEqual(s["electrodes"], 8)
        self.assertLessEqual(s["spike_count"], 8 * 64)

    def test_refractory(self):
        t = SpikeTensor(2, 10, baseline_rate=1.0, refractory_bins=3)
        t.apply_refractory()
        for e in range(2):
            last = -99
            for b in range(10):
                if t.data[e * 10 + b] == 1:
                    self.assertGreaterEqual(b - last, 3)
                    last = b


class TestControlLoop(unittest.TestCase):
    def test_solves_default_maze(self):
        self.assertTrue(ControlLoop(6, 6, 32).run(max_steps=40)["solved"])


class TestAdversarial(unittest.TestCase):
    def test_catastrophic_flagged(self):
        r = adversarial_stress_test(8, 32)
        cat = next(a for a in r["attacks"] if a["name"] == "impulse-catastrophic")
        self.assertTrue(cat["detected"])


class TestIntegration(unittest.TestCase):
    def test_harness(self):
        r = validate_cognitive_robotics(8, 32)
        self.assertIn("passed", r)


if __name__ == "__main__":
    unittest.main(verbosity=2)