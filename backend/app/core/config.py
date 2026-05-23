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
    db_url: str = "sqlite+aiosqlite:///./farmfusion.db"

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

    secret_key: str = "CHANGEME"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    firebase_project_id: Optional[str] = None
    firebase_credentials_path: Optional[str] = None
    firebase_credentials_json: Optional[str] = None
    OPENWEATHER_API_KEY: Optional[str] = None
    WEATHER_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: Optional[str] = None
    MANDI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: Optional[str] = None
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
