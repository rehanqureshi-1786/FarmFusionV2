"""
Application configuration using Pydantic Settings.
Loads environment variables and validates them.
"""
from typing import List, Optional, Union
from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = "FarmFusion API"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # Database
    database_url: PostgresDsn

    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # API Keys
    weather_api_key: Optional[str] = None
    mandi_api_key: Optional[str] = None
    sms_api_key: Optional[str] = None
    storage_api_key: Optional[str] = None

    # CORS
    cors_origins: str = "http://localhost:3000"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    # File Upload
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    upload_dir: str = "uploads"

    @property
    def sync_database_url(self) -> str:
        """Get synchronous database URL for Alembic."""
        url = str(self.database_url)
        # Convert asyncpg to psycopg2 for sync operations
        return url.replace("postgresql+asyncpg://", "postgresql://").replace(
            "postgresql://", "postgresql+psycopg2://"
        )

    @property
    def async_database_url(self) -> str:
        """Get async database URL."""
        url = str(self.database_url)
        if "postgresql+asyncpg" not in url:
            return url.replace("postgresql://", "postgresql+asyncpg://")
        return url


# Global settings instance
settings = Settings()
