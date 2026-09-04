from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.api.config import settings
from apps.api.routes import (
    auth,
    researcher,
    projects,
    memory,
    sources,
    documents,
    search,
    research,
    papers,
    skills,
    mcp,
    integrations,
    automation,
    models,
    energy,
    analytics,
    system,
)

app = FastAPI(
    title="Anvaya AI OS",
    description="Researcher-Aware Intelligence Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(researcher.router, prefix="/api/v1/researcher", tags=["Researcher"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(memory.router, prefix="/api/v1/memory", tags=["Memory"])
app.include_router(sources.router, prefix="/api/v1/sources", tags=["Sources"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(search.router, prefix="/api/v1/search", tags=["Search"])
app.include_router(research.router, prefix="/api/v1/research", tags=["Research"])
app.include_router(papers.router, prefix="/api/v1/papers", tags=["Papers"])
app.include_router(skills.router, prefix="/api/v1/skills", tags=["Skills"])
app.include_router(mcp.router, prefix="/api/v1/mcp", tags=["MCP"])
app.include_router(integrations.router, prefix="/api/v1/integrations", tags=["Integrations"])
app.include_router(automation.router, prefix="/api/v1/automation", tags=["Automation"])
app.include_router(models.router, prefix="/api/v1/models", tags=["Models"])
app.include_router(energy.router, prefix="/api/v1/energy", tags=["Energy"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(system.router, prefix="/api/v1/system", tags=["System"])


@app.get("/")
async def root():
    return {
        "name": "Anvaya AI OS",
        "version": "1.0.0",
        "description": "Researcher-Aware Intelligence Platform",
        "status": "operational",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
