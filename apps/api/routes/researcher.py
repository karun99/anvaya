from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from apps.api.database import get_db
from apps.api.models import ResearcherProfile, User
from apps.api.routes.auth import get_current_user

router = APIRouter()


class ProfileUpdate(BaseModel):
    interests: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    projects: Optional[List[str]] = None
    publications: Optional[List[dict]] = None
    research_goals: Optional[List[str]] = None
    preferred_sources: Optional[List[str]] = None
    preferred_models: Optional[List[str]] = None
    preferred_languages: Optional[List[str]] = None
    privacy_preferences: Optional[dict] = None


class ProfileResponse(BaseModel):
    id: str
    user_id: str
    interests: List[str]
    skills: List[str]
    projects: List[str]
    publications: List[dict]
    research_goals: List[str]
    preferred_sources: List[str]
    preferred_models: List[str]
    preferred_languages: List[str]
    privacy_preferences: dict
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ResearcherProfile).where(ResearcherProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        profile = ResearcherProfile(user_id=current_user.id)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    return profile


@router.put("/profile", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ResearcherProfile).where(ResearcherProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        profile = ResearcherProfile(user_id=current_user.id)
        db.add(profile)

    update_data = profile_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)
    return profile


@router.get("/twin")
async def get_researcher_twin(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ResearcherProfile).where(ResearcherProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        return {
            "interests": [],
            "projects": [],
            "skills": [],
            "publications": [],
            "research_goals": [],
            "preferred_sources": [],
        }

    return {
        "interests": profile.interests or [],
        "projects": profile.projects or [],
        "skills": profile.skills or [],
        "publications": profile.publications or [],
        "research_goals": profile.research_goals or [],
        "preferred_sources": profile.preferred_sources or [],
        "preferred_models": profile.preferred_models or [],
        "preferred_languages": profile.preferred_languages or [],
    }
