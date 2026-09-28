import os
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    PROJECT_NAME: str = "ALBUYBA AUTHENTIC MANDI"
    VERSION: str = "2.5.0"
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "postgresql://postgres:root@localhost:5432/mandi_opsdesk"
    SECRET_KEY: str = "super_secret_mandi_ops_key_production_2026_change_me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ENFORCE_AUTH: bool = True
    
    CORS_ORIGINS: Union[str, List[str]] = os.getenv("CORS_ORIGINS","http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173").strip(",")
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # @field_validator("CORS_ORIGINS", mode="before")
    # @classmethod
    # def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
    #     # Fallback check if user entered CORS_ORIGIN or CORES_ORIGIN in Render
    #     raw_val = (
    #         v 
    #         or os.getenv("CORS_ORIGINS")
    #     )
    #     if isinstance(raw_val, str) and not raw_val.startswith("["):
    #         # Strip whitespace and trailing slashes from each origin
    #         return [i.strip().rstrip("/") for i in raw_val.split(",") if i.strip()]
    #     elif isinstance(raw_val, list):
    #         return [str(i).strip().rstrip("/") for i in raw_val]
    #     return ["*"]

settings = Settings()