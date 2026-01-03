"""Application configuration using Pydantic Settings"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    database_url: str

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60  # 1 hour as per spec (plan.md operational parameters)

    # CORS
    cors_origins: List[str] = ["*"]

    # Application
    app_name: str = "Todo Web Application"
    app_version: str = "1.0.0"
    environment: str = "development"

    # AI Provider Configuration (Groq)
    groq_api_key: str
    groq_model: str = "openai/gpt-oss-20b"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


settings = Settings()
