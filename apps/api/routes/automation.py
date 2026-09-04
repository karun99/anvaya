from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

from apps.api.database import get_db
from apps.api.models import Webhook, User
from apps.api.routes.auth import get_current_user

router = APIRouter()


class WebhookCreate(BaseModel):
    name: str
    url: str
    events: List[str]
    secret: Optional[str] = None


class WebhookResponse(BaseModel):
    id: str
    user_id: str
    name: str
    url: str
    events: List[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[WebhookResponse])
async def list_webhooks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Webhook).where(Webhook.user_id == current_user.id)
    )
    return result.scalars().all()


@router.post("/", response_model=WebhookResponse)
async def create_webhook(
    webhook: WebhookCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    db_webhook = Webhook(
        user_id=current_user.id,
        name=webhook.name,
        url=webhook.url,
        events=webhook.events,
        secret=webhook.secret,
    )
    db.add(db_webhook)
    await db.commit()
    await db.refresh(db_webhook)
    return db_webhook


@router.delete("/{webhook_id}")
async def delete_webhook(
    webhook_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from fastapi import HTTPException
    result = await db.execute(
        select(Webhook).where(
            Webhook.id == webhook_id,
            Webhook.user_id == current_user.id,
        )
    )
    webhook = result.scalar_one_or_none()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    await db.delete(webhook)
    await db.commit()
    return {"status": "deleted"}
