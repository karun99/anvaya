from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

from apps.api.database import get_db
from apps.api.models import Source, User
from apps.api.routes.auth import get_current_user

router = APIRouter()


class SourceCreate(BaseModel):
    title: str
    url: Optional[str] = None
    source_type: str
    author: Optional[str] = None
    doi: Optional[str] = None
    publisher: Optional[str] = None
    published_at: Optional[datetime] = None
    content_hash: Optional[str] = None
    quality_score: float = 0.0
    visibility: str = "PRIVATE"
    metadata_: Optional[dict] = None


class SourceUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    source_type: Optional[str] = None
    author: Optional[str] = None
    doi: Optional[str] = None
    publisher: Optional[str] = None
    published_at: Optional[datetime] = None
    quality_score: Optional[float] = None
    visibility: Optional[str] = None
    metadata_: Optional[dict] = None


class SourceResponse(BaseModel):
    id: str
    user_id: str
    title: str
    url: Optional[str]
    source_type: str
    author: Optional[str]
    doi: Optional[str]
    publisher: Optional[str]
    published_at: Optional[datetime]
    retrieved_at: datetime
    content_hash: Optional[str]
    quality_score: float
    visibility: str
    metadata_: dict
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[SourceResponse])
async def list_sources(
    source_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Source).where(Source.user_id == current_user.id)
    if source_type:
        query = query.where(Source.source_type == source_type)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=SourceResponse)
async def create_source(
    source: SourceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    db_source = Source(
        user_id=current_user.id,
        title=source.title,
        url=source.url,
        source_type=source.source_type,
        author=source.author,
        doi=source.doi,
        publisher=source.publisher,
        published_at=source.published_at,
        content_hash=source.content_hash,
        quality_score=source.quality_score,
        visibility=source.visibility,
        metadata_=source.metadata_ or {},
    )
    db.add(db_source)
    await db.commit()
    await db.refresh(db_source)
    return db_source


@router.get("/{source_id}", response_model=SourceResponse)
async def get_source(
    source_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Source).where(
            Source.id == source_id,
            Source.user_id == current_user.id,
        )
    )
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


@router.put("/{source_id}", response_model=SourceResponse)
async def update_source(
    source_id: uuid.UUID,
    source_data: SourceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Source).where(
            Source.id == source_id,
            Source.user_id == current_user.id,
        )
    )
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    update_data = source_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(source, field, value)

    await db.commit()
    await db.refresh(source)
    return source


@router.delete("/{source_id}")
async def delete_source(
    source_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Source).where(
            Source.id == source_id,
            Source.user_id == current_user.id,
        )
    )
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    await db.delete(source)
    await db.commit()
    return {"status": "deleted"}
