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
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://postgres:root@localhost:5432/mandi_opsdesk"
    
    # Cryptographic JWT Configuration
    SECRET_KEY: str = "super_secret_mandi_ops_key_production_2026_change_me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ENFORCE_AUTH: bool = True
    
    # CORS Origin Whitelist
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173"

    # Server Bindings
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        return ["*"]

settings = Settings()
