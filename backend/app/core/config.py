from typing import List, Optional
import json
from pathlib import Path
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "FarmFusion"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False
    docs_url: Optional[str] = "/docs"
    redoc_url: Optional[str] = "/redoc"
    cors_origins_raw: str = Field(
        "*",
        validation_alias=AliasChoices("CORS_ORIGINS", "ALLOWED_ORIGINS")
    )
    db_url: str = Field(
        "sqlite+aiosqlite:///./farmfusion.db",
        validation_alias=AliasChoices("DB_URL", "DATABASE_URL")
    )
    async_database_url_raw: Optional[str] = Field(None, validation_alias="ASYNC_DATABASE_URL")
    sync_database_url_raw: Optional[str] = Field(None, validation_alias="SYNC_DATABASE_URL")
    version: str = Field("1.0.0", validation_alias="VERSION")

    secret_key: str = Field("CHANGEME", validation_alias="SECRET_KEY")
    algorithm: str = Field("HS256", validation_alias="ALGORITHM")
    access_token_expire_minutes: int = Field(30, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(7, validation_alias="REFRESH_TOKEN_EXPIRE_DAYS")

    # Legacy / Provider API keys
    openai_api_key: Optional[str] = Field(None, validation_alias="OPENAI_API_KEY")
    openai_model: Optional[str] = Field("gpt-3.5-turbo", validation_alias="OPENAI_MODEL")
    groq_api_key: Optional[str] = Field(None, validation_alias="GROQ_API_KEY")
    groq_model: Optional[str] = Field("llama3-8b-8192", validation_alias="GROQ_MODEL")
    groq_vision_model: Optional[str] = Field("llama-3.2-11b-vision-preview", validation_alias="GROQ_VISION_MODEL")
    gemini_api_key: Optional[str] = Field(None, validation_alias="GEMINI_API_KEY")
    gemini_model: Optional[str] = Field("gemini-1.5-flash", validation_alias="GEMINI_MODEL")
    openweather_api_key: Optional[str] = Field(None, validation_alias="OPENWEATHER_API_KEY")
    weather_api_key: Optional[str] = Field(None, validation_alias="WEATHER_API_KEY")
    mandi_api_key: Optional[str] = Field(None, validation_alias="MANDI_API_KEY")
    firebase_project_id: Optional[str] = Field(None, validation_alias="FIREBASE_PROJECT_ID")
    firebase_credentials_path: Optional[str] = Field(None, validation_alias="FIREBASE_CREDENTIALS_PATH")
    firebase_credentials_json: Optional[str] = Field(None, validation_alias="FIREBASE_CREDENTIALS_JSON")

    # LLM via OpenRouter
    openrouter_api_key: Optional[str] = Field(None, validation_alias="OPENROUTER_API_KEY")
    primary_llm_model: str = Field("google/gemma-3-12b-it", validation_alias="PRIMARY_LLM_MODEL")
    fallback_llm_model: str = Field("qwen/qwen-2.5-7b-instruct", validation_alias="FALLBACK_LLM_MODEL")


    # Bhashini & Voice
    bhashini_user_id: Optional[str] = Field(None, validation_alias="BHASHINI_USER_ID")
    bhashini_api_key: Optional[str] = Field(None, validation_alias="BHASHINI_API_KEY")
    bhashini_pipeline_id: Optional[str] = Field(None, validation_alias="BHASHINI_PIPELINE_ID")

    # Cache & Vector Search
    redis_url: str = Field("redis://localhost:6379/0", validation_alias="REDIS_URL")
    embedding_model_name: str = Field("BAAI/bge-m3", validation_alias="EMBEDDING_MODEL_NAME")

    # Crop Recommendation ML artifacts (trained XGBoost model V2 & V1 fallback)
    crop_model_path: str = Field(
        "app/ml_models/crop/v2/crop_recommendation_v2.joblib",
        validation_alias=AliasChoices("CROP_MODEL_PATH", "CROP_MODEL_V2_PATH"),
    )
    crop_label_encoder_path: str = Field(
        "app/ml_models/crop/v2/crop_label_encoder_v2.joblib",
        validation_alias=AliasChoices("CROP_LABEL_ENCODER_PATH", "CROP_LABEL_ENCODER_V2_PATH"),
    )
    crop_model_metadata_path: str = Field(
        "app/ml_models/crop/v2/crop_model_metadata_v2.json",
        validation_alias=AliasChoices("CROP_MODEL_METADATA_PATH", "CROP_MODEL_V2_METADATA_PATH"),
    )
    crop_model_v1_path: str = Field(
        "app/ml_models/crop_recommendation.joblib",
        validation_alias="CROP_MODEL_V1_PATH",
    )
    crop_label_encoder_v1_path: str = Field(
        "app/ml_models/crop_label_encoder.joblib",
        validation_alias="CROP_LABEL_ENCODER_V1_PATH",
    )
    crop_model_metadata_v1_path: str = Field(
        "app/ml_models/crop_model_metadata.json",
        validation_alias="CROP_MODEL_METADATA_V1_PATH",
    )

    # Disease Detection ML artifacts (trained EfficientNet-B3 model)
    disease_model_path: str = Field(
        "app/ml_models/disease/v2/disease_model_v2_38class.pth",
        validation_alias=AliasChoices("DISEASE_MODEL_PATH", "DISEASE_MODEL_V2_PATH"),
    )
    disease_label_mapping_path: str = Field(
        "app/ml_models/disease/v2/disease_label_mapping_v2_38class.json",
        validation_alias=AliasChoices("DISEASE_LABEL_MAPPING_PATH", "DISEASE_LABEL_MAPPING_V2_PATH"),
    )
    disease_model_metadata_path: str = Field(
        "app/ml_models/disease/v2/disease_model_metadata_v2_38class.json",
        validation_alias=AliasChoices("DISEASE_MODEL_METADATA_PATH", "DISEASE_MODEL_V2_METADATA_PATH"),
    )
    disease_model_v1_path: str = Field(
        "app/ml_models/disease/v1/disease_model_v1.pth",
        validation_alias="DISEASE_MODEL_V1_PATH",
    )
    disease_label_mapping_v1_path: str = Field(
        "app/ml_models/disease/v1/disease_label_mapping.json",
        validation_alias="DISEASE_LABEL_MAPPING_V1_PATH",
    )
    disease_model_v1_metadata_path: str = Field(
        "app/ml_models/disease/v1/disease_model_metadata.json",
        validation_alias="DISEASE_MODEL_V1_METADATA_PATH",
    )

    # Soil Data Service (SoilGrids/ISRIC) for the "No Soil Report" flow
    # SoilGrids requires no API key - it's a free public API
    # No configuration needed for SoilGrids integration


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
