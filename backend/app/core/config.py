from typing import List, Optional
import json
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "FarmFusion"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False
    docs_url: Optional[str] = "/docs"
    redoc_url: Optional[str] = "/redoc"
    cors_origins_raw: str = Field("*", env="CORS_ORIGINS")
    db_url: str = Field("sqlite+aiosqlite:///./farmfusion.db", env="DB_URL")
    async_database_url_raw: Optional[str] = Field(None, env="ASYNC_DATABASE_URL")
    sync_database_url_raw: Optional[str] = Field(None, env="SYNC_DATABASE_URL")
    version: str = Field("1.0.0", env="VERSION")

    secret_key: str = Field("CHANGEME", env="SECRET_KEY")
    algorithm: str = Field("HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    firebase_project_id: Optional[str] = Field(None, env="FIREBASE_PROJECT_ID")
    firebase_credentials_path: Optional[str] = Field(None, env="FIREBASE_CREDENTIALS_PATH")
    firebase_credentials_json: Optional[str] = Field(None, env="FIREBASE_CREDENTIALS_JSON")
    openweather_api_key: Optional[str] = Field(None, env="OPENWEATHER_API_KEY")
    weather_api_key: Optional[str] = Field(None, env="WEATHER_API_KEY")
    groq_api_key: Optional[str] = Field(None, env="GROQ_API_KEY")
    groq_model: Optional[str] = Field(None, env="GROQ_MODEL")
    groq_vision_model: Optional[str] = Field(None, env="GROQ_VISION_MODEL")
    mandi_api_key: Optional[str] = Field(None, env="MANDI_API_KEY")
    gemini_api_key: Optional[str] = Field(None, env="GEMINI_API_KEY")
    gemini_model: Optional[str] = Field(None, env="GEMINI_MODEL")
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    openai_model: Optional[str] = Field(None, env="OPENAI_MODEL")

    @property
    def cors_origins(self) -> List[str]:
        value = self.cors_origins_raw
        if isinstance(value, list):
            return [str(item) for item in value]
        value = str(value).strip()
        if not value:
            return ["*"]
        try:
            parsed = json.loads(value)
            if isinstance(parsed, str):
                return [parsed]
            if isinstance(parsed, list):
                return [str(item) for item in parsed]
        except json.JSONDecodeError:
            pass
        return [item.strip() for item in value.split(",") if item.strip()]

    @property
    def effective_async_database_url(self) -> str:
        if self.async_database_url_raw:
            return self.async_database_url_raw
        if self.db_url.startswith("sqlite+aiosqlite://"):
            return self.db_url
        if self.db_url.startswith("sqlite://"):
            return self.db_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
        return self.db_url

    @property
    def database_url(self) -> str:
        return self.db_url

    @property
    def allowed_origins(self) -> List[str]:
        return self.cors_origins

    @property
    def sync_database_url(self) -> str:
        if self.sync_database_url_raw:
            return self.sync_database_url_raw
        if self.db_url.startswith("sqlite+aiosqlite://"):
            return self.db_url.replace("sqlite+aiosqlite://", "sqlite://", 1)
        return self.db_url

    @property
    def GEMINI_API_KEY(self) -> Optional[str]:
        return self.gemini_api_key

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[2] / '.env'),
        env_file_encoding='utf-8',
        extra='allow',
    )

settings = Settings()


def get_settings() -> Settings:
    return settings


def get_db_url() -> str:
    return settings.db_url


def is_using_postgres() -> bool:
    return settings.db_url.startswith("postgres")
