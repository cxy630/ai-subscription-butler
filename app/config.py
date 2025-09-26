"""
Application Configuration Management
"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application
    app_name: str = Field(default="AI Subscription Butler", env="APP_NAME")
    app_env: str = Field(default="development", env="APP_ENV")
    app_debug: bool = Field(default=True, env="APP_DEBUG")
    app_url: str = Field(default="http://localhost:8501", env="APP_URL")
    secret_key: str = Field(default="dev-secret-key-change-in-production", env="SECRET_KEY")

    # Database
    database_url: str = Field(default="sqlite:///data/subscriptions.db", env="DATABASE_URL")
    db_pool_size: int = Field(default=5, env="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=10, env="DB_MAX_OVERFLOW")

    # OpenAI
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_org_id: Optional[str] = Field(default=None, env="OPENAI_ORG_ID")
    openai_model_chat: str = Field(default="gpt-3.5-turbo", env="OPENAI_MODEL_CHAT")
    openai_model_complex: str = Field(default="gpt-4", env="OPENAI_MODEL_COMPLEX")
    openai_model_vision: str = Field(default="gpt-4-vision-preview", env="OPENAI_MODEL_VISION")
    openai_max_tokens: int = Field(default=1000, env="OPENAI_MAX_TOKENS")
    openai_temperature: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    openai_request_timeout: int = Field(default=30, env="OPENAI_REQUEST_TIMEOUT")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_ttl: int = Field(default=3600, env="REDIS_TTL")

    # Features
    feature_ai_chat: bool = Field(default=True, env="FEATURE_AI_CHAT")
    feature_ocr: bool = Field(default=True, env="FEATURE_OCR")
    feature_analytics: bool = Field(default=True, env="FEATURE_ANALYTICS")
    feature_reminders: bool = Field(default=True, env="FEATURE_REMINDERS")
    feature_family_sharing: bool = Field(default=False, env="FEATURE_FAMILY_SHARING")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="text", env="LOG_FORMAT")
    log_file: str = Field(default="logs/app.log", env="LOG_FILE")
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")

    # Security
    session_lifetime: int = Field(default=86400, env="SESSION_LIFETIME")  # 24 hours
    cors_origins: str = Field(default="http://localhost:3000,https://localhost:3000", env="CORS_ORIGINS")
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_period: int = Field(default=60, env="RATE_LIMIT_PERIOD")

    # Storage
    upload_max_size: int = Field(default=5242880, env="UPLOAD_MAX_SIZE")  # 5MB
    upload_allowed_extensions: str = Field(default=".jpg,.jpeg,.png,.pdf", env="UPLOAD_ALLOWED_EXTENSIONS")
    storage_backend: str = Field(default="local", env="STORAGE_BACKEND")

    # Paths
    @property
    def project_root(self) -> Path:
        """Get project root directory."""
        return Path(__file__).parent.parent

    @property
    def data_dir(self) -> Path:
        """Get data directory."""
        return self.project_root / "data"

    @property
    def logs_dir(self) -> Path:
        """Get logs directory."""
        return self.project_root / "logs"

    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def upload_allowed_extensions_list(self) -> List[str]:
        """Get allowed file extensions as list."""
        return [ext.strip() for ext in self.upload_allowed_extensions.split(",")]

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app_env == "production"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Create global settings instance
settings = Settings()

# Ensure required directories exist
settings.data_dir.mkdir(parents=True, exist_ok=True)
settings.logs_dir.mkdir(parents=True, exist_ok=True)