from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional

from apps.api.database import get_db
from apps.api.models import ModelConfig, User
from apps.api.routes.auth import get_current_user

router = APIRouter()


class ModelConfigCreate(BaseModel):
    task: str
    provider: str
    model: str
    endpoint: Optional[str] = None
    api_key: Optional[str] = None
    parameters: Optional[dict] = None


class ModelConfigResponse(BaseModel):
    id: str
    user_id: str
    task: str
    provider: str
    model: str
    endpoint: Optional[str]
    parameters: dict
    is_active: bool

    class Config:
        from_attributes = True


@router.get("/", response_model=List[ModelConfigResponse])
async def list_model_configs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ModelConfig).where(ModelConfig.user_id == current_user.id)
    )
    return result.scalars().all()


@router.post("/", response_model=ModelConfigResponse)
async def create_model_config(
    config: ModelConfigCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    db_config = ModelConfig(
        user_id=current_user.id,
        task=config.task,
        provider=config.provider,
        model=config.model,
        endpoint=config.endpoint,
        api_key=config.api_key,
        parameters=config.parameters or {},
    )
    db.add(db_config)
    await db.commit()
    await db.refresh(db_config)
    return db_config
