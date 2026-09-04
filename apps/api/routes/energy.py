from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from apps.api.database import get_db
from apps.api.models import User
from apps.api.routes.auth import get_current_user

router = APIRouter()


class EnergyModeUpdate(BaseModel):
    mode: str


class EnergyStatus(BaseModel):
    mode: str
    llm_requests: int
    tokens_used: int
    embedding_operations: int
    documents_processed: int
    cache_hits: int
    cache_misses: int
    local_vs_cloud: dict
    estimated_footprint: str


@router.get("/status", response_model=EnergyStatus)
async def get_energy_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select, func
    from apps.api.models import UsageEvent

    result = await db.execute(
        select(func.count(UsageEvent.id)).where(UsageEvent.user_id == current_user.id)
    )
    total_events = result.scalar() or 0

    return EnergyStatus(
        mode="BALANCED",
        llm_requests=total_events,
        tokens_used=0,
        embedding_operations=0,
        documents_processed=0,
        cache_hits=0,
        cache_misses=0,
        local_vs_cloud={"local": 0, "cloud": 0},
        estimated_footprint="Low - Initial setup",
    )


@router.put("/mode")
async def update_energy_mode(
    mode: EnergyModeUpdate,
    current_user: User = Depends(get_current_user),
):
    valid_modes = ["PERFORMANCE", "BALANCED", "ENERGY_SAVER", "LOCAL_FIRST", "OFFLINE"]
    if mode.mode not in valid_modes:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mode. Must be one of: {', '.join(valid_modes)}",
        )

    return {"mode": mode.mode, "status": "updated"}
