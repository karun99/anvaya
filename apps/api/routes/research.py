from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from apps.api.database import get_db
from apps.api.models import User
from apps.api.routes.auth import get_current_user

router = APIRouter()


class ResearchRequest(BaseModel):
    question: str
    use_memory: bool = True
    project_id: Optional[str] = None


class EvidenceItem(BaseModel):
    source: str
    content: str
    relevance: float
    source_type: str


class ResearchResponse(BaseModel):
    question: str
    answer: str
    evidence: List[EvidenceItem]
    sources: List[dict]
    confidence: float
    timestamp: datetime


@router.post("/", response_model=ResearchResponse)
async def conduct_research(
    request: ResearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    from apps.api.models import Memory, Source

    context = []
    if request.use_memory:
        memory_query = select(Memory).where(Memory.user_id == current_user.id)
        if request.project_id:
            memory_query = memory_query.where(Memory.project_id == request.project_id)
        memory_result = await db.execute(memory_query.limit(50))
        memories = memory_result.scalars().all()
        context = [m.content for m in memories]

    source_query = (
        select(Source)
        .where(Source.user_id == current_user.id)
        .where(Source.title.ilike(f"%{request.question}%"))
        .limit(10)
    )
    source_result = await db.execute(source_query)
    sources = source_result.scalars().all()

    evidence = [
        EvidenceItem(
            source=source.title,
            content=f"Source: {source.title} by {source.author or 'Unknown'}",
            relevance=source.quality_score,
            source_type=source.source_type,
        )
        for source in sources
    ]

    context_str = "\n".join(context) if context else "No research memory available."
    sources_str = "\n".join([f"- {s.title}" for s in sources]) if sources else "No sources found."

    return ResearchResponse(
        question=request.question,
        answer=f"Based on your research context and available sources:\n\n"
               f"Research Context:\n{context_str}\n\n"
               f"Relevant Sources:\n{sources_str}\n\n"
               f"Analysis of '{request.question}' requires further AI processing.",
        evidence=evidence,
        sources=[{"title": s.title, "url": s.url} for s in sources],
        confidence=0.5,
        timestamp=datetime.utcnow(),
    )
