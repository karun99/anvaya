import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Anvaya AI OS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/anvaya",
    )

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # LLM Provider
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4")

    # Embedding
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "openai")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    EMBEDDING_DIMENSIONS: int = 1536

    # External Services
    AGENT_REACH_ENDPOINT: str = os.getenv("AGENT_REACH_ENDPOINT", "")
    OCR_ENDPOINT: str = os.getenv("OCR_ENDPOINT", "")

    # MCP
    MCP_ENABLED: bool = os.getenv("MCP_ENABLED", "false").lower() == "true"

    # Automation
    N8N_WEBHOOK_URL: str = os.getenv("N8N_WEBHOOK_URL", "")
    MAKE_WEBHOOK_URL: str = os.getenv("MAKE_WEBHOOK_URL", "")

    # Energy
    ENERGY_MODE: str = os.getenv("ENERGY_MODE", "BALANCED")

    # Cache
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))

    # Workers
    WORKER_ENABLED: bool = os.getenv("WORKER_ENABLED", "true").lower() == "true"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
