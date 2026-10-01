import os
from pathlib import Path
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Locate .env dynamically regardless of current working directory
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BACKEND_DIR / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH) if ENV_PATH.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore"
    )

    PROJECT_NAME: str = "ALBUYBA AUTHENTIC MANDI"
    VERSION: str = "2.5.0"
    ENVIRONMENT: str = "development"

    # Database Configuration (Supplied strictly via environment)
    DATABASE_URL: str

    # Security & JWT (Supplied strictly via environment)
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ENFORCE_AUTH: bool = True

    # CORS
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://localhost:5173"

    # Server Bindings
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_database_url(cls, v: str) -> str:
        if not v:
            raise ValueError("DATABASE_URL environment variable is required")
        # Ensure Neon/Render postgres:// is normalized to postgresql://
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql://", 1)
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            origins = [o.strip().rstrip("/") for o in v.split(",") if o.strip()]
            return origins if origins else ["*"]
        elif isinstance(v, list):
            return [str(o).strip().rstrip("/") for o in v if str(o).strip()]
        return ["*"]

settings = Settings()