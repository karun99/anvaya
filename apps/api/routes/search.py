from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional

from apps.api.database import get_db
from apps.api.models import User
from apps.api.routes.auth import get_current_user

router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    personalized: bool = True
    limit: int = 10
    source_type: Optional[str] = None


class SearchSource(BaseModel):
    title: str
    url: Optional[str]
    source_type: str
    author: Optional[str]
    score: float
    metadata: dict


class SearchResponse(BaseModel):
    query: str
    sources: List[SearchSource]
    count: int
    personalized: bool


@router.post("/", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    from apps.api.models import Source

    query = select(Source).where(Source.user_id == current_user.id)

    if request.source_type:
        query = query.where(Source.source_type == request.source_type)

    query = query.where(
        Source.title.ilike(f"%{request.query}%")
    ).limit(request.limit)

    result = await db.execute(query)
    sources = result.scalars().all()

    search_sources = [
        SearchSource(
            title=source.title,
            url=source.url,
            source_type=source.source_type,
            author=source.author,
            score=source.quality_score,
            metadata=source.metadata_ or {},
        )
        for source in sources
    ]

    return SearchResponse(
        query=request.query,
        sources=search_sources,
        count=len(search_sources),
        personalized=request.personalized,
    )
