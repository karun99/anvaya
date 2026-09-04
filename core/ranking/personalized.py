from typing import List, Optional
from dataclasses import dataclass


@dataclass
class RankedResult:
    id: str
    content: str
    score: float
    query_similarity: float
    researcher_relevance: float
    source_quality: float
    recency: float
    metadata: dict


class PersonalizedRanker:
    def __init__(
        self,
        query_weight: float = 0.50,
        researcher_weight: float = 0.30,
        quality_weight: float = 0.10,
        recency_weight: float = 0.10,
    ):
        self.query_weight = query_weight
        self.researcher_weight = researcher_weight
        self.quality_weight = quality_weight
        self.recency_weight = recency_weight

    def rank(
        self,
        results: List[dict],
        query: str,
        researcher_context: Optional[dict] = None,
    ) -> List[RankedResult]:
        ranked = []
        for result in results:
            query_sim = result.get("query_similarity", 0.0)
            research_rel = self._calculate_researcher_relevance(
                result, researcher_context
            )
            quality = result.get("quality_score", 0.0)
            recency = self._calculate_recency(result)

            final_score = (
                self.query_weight * query_sim
                + self.researcher_weight * research_rel
                + self.quality_weight * quality
                + self.recency_weight * recency
            )

            ranked.append(
                RankedResult(
                    id=result.get("id", ""),
                    content=result.get("content", ""),
                    score=final_score,
                    query_similarity=query_sim,
                    researcher_relevance=research_rel,
                    source_quality=quality,
                    recency=recency,
                    metadata=result.get("metadata", {}),
                )
            )

        return sorted(ranked, key=lambda x: x.score, reverse=True)

    def _calculate_researcher_relevance(
        self, result: dict, researcher_context: Optional[dict]
    ) -> float:
        if not researcher_context:
            return 0.0

        interests = researcher_context.get("interests", [])
        content = result.get("content", "").lower()

        relevance = 0.0
        for interest in interests:
            if interest.lower() in content:
                relevance += 0.2

        return min(relevance, 1.0)

    def _calculate_recency(self, result: dict) -> float:
        from datetime import datetime

        created_at = result.get("created_at")
        if not created_at:
            return 0.0

        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at)
            except ValueError:
                return 0.0

        days_old = (datetime.utcnow() - created_at).days
        if days_old < 7:
            return 1.0
        elif days_old < 30:
            return 0.8
        elif days_old < 90:
            return 0.6
        elif days_old < 365:
            return 0.4
        else:
            return 0.2
