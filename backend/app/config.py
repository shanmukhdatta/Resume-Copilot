"""Centralized application configuration."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "AI Resume Copilot"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    API_PREFIX: str = "/api/v1"

    # LLM
    LLM_PROVIDER: str = "gemini"
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-1.5-flash"
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    LLM_TEMPERATURE: float = 0.4
    LLM_MAX_RETRIES: int = 2
    LLM_TIMEOUT_SECONDS: int = 60

    # Storage
    UPLOAD_DIR: str = "data/uploads"
    PARSED_DIR: str = "data/parsed"
    GENERATED_DIR: str = "data/generated"
    EXPORT_DIR: str = "data/exports"
    CACHE_DIR: str = "data/cache"
    MAX_UPLOAD_SIZE_MB: int = 10

    # Database (optional)
    DATABASE_URL: str | None = None

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "logs"

    # Validation thresholds
    MIN_ATS_SCORE: float = 60.0
    MAX_VALIDATION_RETRIES: int = 2

    # CORS
    ALLOWED_ORIGINS: list[str] = ["*"]


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (singleton)."""
    return Settings()
