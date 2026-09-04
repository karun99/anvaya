from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

from apps.api.database import get_db
from apps.api.models import Memory, User
from apps.api.routes.auth import get_current_user

router = APIRouter()


class MemoryCreate(BaseModel):
    type: str
    content: str
    project_id: Optional[str] = None
    source_id: Optional[str] = None
    confidence: float = 0.0
    importance: float = 0.0
    source_reference: Optional[str] = None
    user_verified: bool = False
    visibility: str = "PRIVATE"
    metadata_: Optional[dict] = None


class MemoryUpdate(BaseModel):
    type: Optional[str] = None
    content: Optional[str] = None
    confidence: Optional[float] = None
    importance: Optional[float] = None
    source_reference: Optional[str] = None
    user_verified: Optional[bool] = None
    visibility: Optional[str] = None
    metadata_: Optional[dict] = None


class MemoryResponse(BaseModel):
    id: str
    user_id: str
    project_id: Optional[str]
    source_id: Optional[str]
    type: str
    content: str
    confidence: float
    importance: float
    source_reference: Optional[str]
    user_verified: bool
    visibility: str
    metadata_: dict
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[MemoryResponse])
async def list_memories(
    memory_type: Optional[str] = None,
    project_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Memory).where(Memory.user_id == current_user.id)
    if memory_type:
        query = query.where(Memory.type == memory_type)
    if project_id:
        query = query.where(Memory.project_id == project_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=MemoryResponse)
async def create_memory(
    memory: MemoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    db_memory = Memory(
        user_id=current_user.id,
        type=memory.type,
        content=memory.content,
        project_id=memory.project_id,
        source_id=memory.source_id,
        confidence=memory.confidence,
        importance=memory.importance,
        source_reference=memory.source_reference,
        user_verified=memory.user_verified,
        visibility=memory.visibility,
        metadata_=memory.metadata_ or {},
    )
    db.add(db_memory)
    await db.commit()
    await db.refresh(db_memory)
    return db_memory


@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(
    memory_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Memory).where(
            Memory.id == memory_id,
            Memory.user_id == current_user.id,
        )
    )
    memory = result.scalar_one_or_none()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory


@router.put("/{memory_id}", response_model=MemoryResponse)
async def update_memory(
    memory_id: uuid.UUID,
    memory_data: MemoryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Memory).where(
            Memory.id == memory_id,
            Memory.user_id == current_user.id,
        )
    )
    memory = result.scalar_one_or_none()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")

    update_data = memory_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(memory, field, value)

    await db.commit()
    await db.refresh(memory)
    return memory


@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Memory).where(
            Memory.id == memory_id,
            Memory.user_id == current_user.id,
        )
    )
    memory = result.scalar_one_or_none()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")

    await db.delete(memory)
    await db.commit()
    return {"status": "deleted"}


@router.post("/search")
async def search_memories(
    query: str,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Memory).where(
            Memory.user_id == current_user.id,
            Memory.content.ilike(f"%{query}%"),
        ).limit(limit)
    )
    memories = result.scalars().all()
    return {"memories": memories, "count": len(memories)}
