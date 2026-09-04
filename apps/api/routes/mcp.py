from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

from apps.api.database import get_db
from apps.api.models import MCPServer, User
from apps.api.routes.auth import get_current_user

router = APIRouter()


class MCPServerCreate(BaseModel):
    name: str
    description: Optional[str] = None
    server_url: str
    authentication: Optional[dict] = None
    tools: Optional[List[dict]] = None
    resources: Optional[List[dict]] = None
    permissions: Optional[dict] = None
    timeout: int = 30
    environment: Optional[dict] = None


class MCPServerResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str]
    server_url: str
    authentication: dict
    tools: List[dict]
    resources: List[dict]
    permissions: dict
    timeout: int
    environment: dict
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[MCPServerResponse])
async def list_mcp_servers(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MCPServer).where(MCPServer.user_id == current_user.id)
    )
    return result.scalars().all()


@router.post("/", response_model=MCPServerResponse)
async def create_mcp_server(
    server: MCPServerCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    db_server = MCPServer(
        user_id=current_user.id,
        name=server.name,
        description=server.description,
        server_url=server.server_url,
        authentication=server.authentication or {},
        tools=server.tools or [],
        resources=server.resources or [],
        permissions=server.permissions or {},
        timeout=server.timeout,
        environment=server.environment or {},
    )
    db.add(db_server)
    await db.commit()
    await db.refresh(db_server)
    return db_server


@router.get("/{server_id}", response_model=MCPServerResponse)
async def get_mcp_server(
    server_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MCPServer).where(
            MCPServer.id == server_id,
            MCPServer.user_id == current_user.id,
        )
    )
    server = result.scalar_one_or_none()
    if not server:
        raise HTTPException(status_code=404, detail="MCP server not found")
    return server


@router.post("/{server_id}/test")
async def test_mcp_server(
    server_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MCPServer).where(
            MCPServer.id == server_id,
            MCPServer.user_id == current_user.id,
        )
    )
    server = result.scalar_one_or_none()
    if not server:
        raise HTTPException(status_code=404, detail="MCP server not found")

    return {
        "status": "tested",
        "server": server.name,
        "url": server.server_url,
        "result": "Connection test requires MCP client implementation",
    }


@router.put("/{server_id}/toggle")
async def toggle_mcp_server(
    server_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MCPServer).where(
            MCPServer.id == server_id,
            MCPServer.user_id == current_user.id,
        )
    )
    server = result.scalar_one_or_none()
    if not server:
        raise HTTPException(status_code=404, detail="MCP server not found")

    server.is_active = not server.is_active
    await db.commit()

    return {"status": "toggled", "is_active": server.is_active}
