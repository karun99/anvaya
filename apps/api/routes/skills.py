from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

from apps.api.database import get_db
from apps.api.models import Skill, SkillRun, User
from apps.api.routes.auth import get_current_user

router = APIRouter()


class SkillCreate(BaseModel):
    name: str
    description: Optional[str] = None
    input_schema: Optional[dict] = None
    steps: Optional[List[dict]] = None
    output_schema: Optional[dict] = None
    permissions: Optional[dict] = None


class SkillResponse(BaseModel):
    id: str
    user_id: Optional[str]
    name: str
    description: Optional[str]
    input_schema: dict
    steps: List[dict]
    output_schema: dict
    permissions: dict
    is_builtin: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SkillRunRequest(BaseModel):
    skill_id: str
    input_data: dict


class SkillRunResponse(BaseModel):
    run_id: str
    skill_id: str
    status: str
    started_at: datetime


@router.get("/", response_model=List[SkillResponse])
async def list_skills(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Skill).where(
            (Skill.user_id == current_user.id) | (Skill.is_builtin == True)
        )
    )
    return result.scalars().all()


@router.post("/", response_model=SkillResponse)
async def create_skill(
    skill: SkillCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    db_skill = Skill(
        user_id=current_user.id,
        name=skill.name,
        description=skill.description,
        input_schema=skill.input_schema or {},
        steps=skill.steps or [],
        output_schema=skill.output_schema or {},
        permissions=skill.permissions or {},
    )
    db.add(db_skill)
    await db.commit()
    await db.refresh(db_skill)
    return db_skill


@router.post("/run", response_model=SkillRunResponse)
async def run_skill(
    request: SkillRunRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Skill).where(Skill.id == request.skill_id)
    )
    skill = result.scalar_one_or_none()
    if not skill:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Skill not found")

    run = SkillRun(
        skill_id=skill.id,
        user_id=current_user.id,
        input_data=request.input_data,
        status="running",
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)

    return SkillRunResponse(
        run_id=str(run.id),
        skill_id=str(skill.id),
        status=run.status,
        started_at=run.started_at,
    )
