from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()


class IntegrationStatus(BaseModel):
    name: str
    type: str
    enabled: bool
    status: str
    endpoint: Optional[str] = None


@router.get("/", response_model=List[IntegrationStatus])
async def list_integrations():
    return [
        IntegrationStatus(
            name="Agent Reach",
            type="search",
            enabled=False,
            status="not_configured",
            endpoint=None,
        ),
        IntegrationStatus(
            name="Unlimited-OCR",
            type="ocr",
            enabled=False,
            status="not_configured",
            endpoint=None,
        ),
        IntegrationStatus(
            name="GitHub",
            type="source",
            enabled=False,
            status="not_configured",
        ),
        IntegrationStatus(
            name="n8n",
            type="automation",
            enabled=False,
            status="not_configured",
            endpoint=None,
        ),
        IntegrationStatus(
            name="Make",
            type="automation",
            enabled=False,
            status="not_configured",
            endpoint=None,
        ),
    ]


@router.post("/{integration_name}/enable")
async def enable_integration(integration_name: str):
    return {"status": "enabled", "integration": integration_name}


@router.post("/{integration_name}/disable")
async def disable_integration(integration_name: str):
    return {"status": "disabled", "integration": integration_name}
