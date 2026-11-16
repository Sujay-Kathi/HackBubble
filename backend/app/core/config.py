from functools import lru_cache
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    APP_NAME: str = "HackBubble"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = "dev-secret-key-change-in-production-must-be-32-chars-min"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/hackbubble"
    DB_ECHO: bool = False

    # Vector Configurations
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # Providers
    AUTH_PROVIDER: Literal["local", "supabase"] = "local"
    STORAGE_PROVIDER: Literal["local", "supabase", "s3"] = "local"
    LOCAL_STORAGE_DIR: str = "./uploads"

    # Supabase (Optional in local mode)
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_STORAGE_BUCKET: str = "resumes"

    # AI & LLM Provider
    LLM_PROVIDER: Literal["openai", "gemini", "ollama"] = "openai"
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"

    # Scraper
    SCRAPER_USER_AGENT: str = "HackBubble-Bot/1.0 (+https://github.com/Sujay-Kathi/HackBubble)"
    SCRAPER_CONCURRENCY: int = 3

    # Email delivery (SMTP)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "notifications@hackbubble.local"
    SMTP_USE_TLS: bool = True
    SMTP_TIMEOUT_SECONDS: int = 10

    # Background workers
    WORKERS_ENABLED: bool = False
    WORKER_DISPATCH_INTERVAL_SECONDS: int = 30
    WORKER_SCRAPE_INTERVAL_SECONDS: int = 900
    WORKER_EMBEDDING_BACKFILL_INTERVAL_SECONDS: int = 3600
    WORKER_BATCH_SIZE: int = 50

    # Rate limiting (in-memory, per-process)
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_REQUESTS: int = 120
    RATE_LIMIT_WINDOW_SECONDS: int = 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
