from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime
    components: Dict[str, str]


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow(),
        components={
            "api": "operational",
            "database": "operational",
            "llm": "not_configured",
            "mcp": "disabled",
            "workers": "operational",
        },
    )


@router.get("/config")
async def get_system_config():
    return {
        "app_name": "Anvaya AI OS",
        "version": "1.0.0",
        "features": {
            "research_memory": True,
            "personalized_ranking": True,
            "llm_gateway": True,
            "mcp": False,
            "skills": True,
            "automation": True,
            "energy_modes": True,
            "local_ai": False,
        },
        "energy_mode": "BALANCED",
    }
