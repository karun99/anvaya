from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Dict, Any

from apps.api.database import get_db
from apps.api.models import User, Memory, Source, Document, UsageEvent
from apps.api.routes.auth import get_current_user

router = APIRouter()


class AnalyticsResponse(BaseModel):
    total_memories: int
    total_sources: int
    total_documents: int
    memory_types: Dict[str, int]
    source_types: Dict[str, int]
    recent_activity: int


@router.get("/", response_model=AnalyticsResponse)
async def get_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    memories_result = await db.execute(
        select(func.count(Memory.id)).where(Memory.user_id == current_user.id)
    )
    total_memories = memories_result.scalar() or 0

    sources_result = await db.execute(
        select(func.count(Source.id)).where(Source.user_id == current_user.id)
    )
    total_sources = sources_result.scalar() or 0

    documents_result = await db.execute(
        select(func.count(Document.id))
        .join(Source, Document.source_id == Source.id)
        .where(Source.user_id == current_user.id)
    )
    total_documents = documents_result.scalar() or 0

    memory_types_result = await db.execute(
        select(Memory.type, func.count(Memory.id))
        .where(Memory.user_id == current_user.id)
        .group_by(Memory.type)
    )
    memory_types = {row[0]: row[1] for row in memory_types_result.all()}

    source_types_result = await db.execute(
        select(Source.source_type, func.count(Source.id))
        .where(Source.user_id == current_user.id)
        .group_by(Source.source_type)
    )
    source_types = {row[0]: row[1] for row in source_types_result.all()}

    return AnalyticsResponse(
        total_memories=total_memories,
        total_sources=total_sources,
        total_documents=total_documents,
        memory_types=memory_types,
        source_types=source_types,
        recent_activity=0,
    )
