from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

from apps.api.database import get_db
from apps.api.models import Source, Document, DocumentChunk, User
from apps.api.routes.auth import get_current_user

router = APIRouter()


class PaperAnalysis(BaseModel):
    paper_id: str
    title: str
    author: Optional[str]
    abstract: Optional[str]
    methodology: Optional[str]
    dataset: Optional[str]
    results: Optional[str]
    limitations: Optional[str]
    research_opportunities: Optional[str]


class PaperResponse(BaseModel):
    id: str
    title: str
    url: Optional[str]
    author: Optional[str]
    doi: Optional[str]
    source_type: str
    quality_score: float
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[PaperResponse])
async def list_papers(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Source).where(
            Source.user_id == current_user.id,
            Source.source_type.in_(["research_paper", "journal", "conference_paper", "preprint"]),
        )
    )
    return result.scalars().all()


@router.post("/analyze", response_model=PaperAnalysis)
async def analyze_paper(
    paper_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Source).where(
            Source.id == paper_id,
            Source.user_id == current_user.id,
        )
    )
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Paper not found")

    doc_result = await db.execute(
        select(Document).where(Document.source_id == source.id)
    )
    document = doc_result.scalar_one_or_none()

    content = document.content if document else ""

    return PaperAnalysis(
        paper_id=str(source.id),
        title=source.title,
        author=source.author,
        abstract=content[:500] if content else None,
        methodology="Analysis requires AI processing",
        dataset="Analysis requires AI processing",
        results="Analysis requires AI processing",
        limitations="Analysis requires AI processing",
        research_opportunities="Analysis requires AI processing",
    )
