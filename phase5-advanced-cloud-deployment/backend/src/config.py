"""Application configuration using Pydantic Settings"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, validator
from typing import List, Union, Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    database_url: str

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60  # 1 hour as per spec (plan.md operational parameters)

    # CORS - Production-ready configuration
    cors_origins: List[str] = ["http://localhost:3000"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """
        Parse CORS origins from comma-separated string or list

        For production, only allow specific domains.
        For development, allow localhost.
        """
        if isinstance(v, str):
            # Split by comma and strip whitespace
            origins = [origin.strip() for origin in v.split(",") if origin.strip()]

            # Validate origins in production
            environment = os.getenv("ENVIRONMENT", "development")
            if environment == "production":
                # In production, reject wildcard origins
                if "*" in origins:
                    raise ValueError(
                        "Wildcard CORS origins (*) are not allowed in production. "
                        "Please specify exact domains."
                    )
                # Validate that all origins are HTTPS in production
                for origin in origins:
                    if not origin.startswith("https://") and origin != "http://localhost:3000":
                        raise ValueError(
                            f"CORS origin '{origin}' must use HTTPS in production environment"
                        )

            return origins
        return v

    # Application
    app_name: str = "Todo Web Application"
    app_version: str = "1.0.0"
    environment: str = "development"

    # AI Provider Configuration (Groq)
    groq_api_key: str
    groq_model: str = "openai/gpt-oss-20b"

    # Redis (optional)
    redis_url: Optional[str] = None

    # Kafka (optional)
    kafka_bootstrap_servers: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


def validate_environment() -> None:
    """
    Validate all required environment variables on startup

    Raises:
        ValueError: If any required environment variable is missing or invalid
    """
    required_vars = {
        "DATABASE_URL": "Database connection string",
        "JWT_SECRET_KEY": "JWT secret key for authentication",
        "GROQ_API_KEY": "Groq API key for AI features",
    }

    missing_vars = []
    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        if not value or value.strip() == "":
            missing_vars.append(f"{var_name} ({description})")

    if missing_vars:
        raise ValueError(
            f"Missing required environment variables:\n" +
            "\n".join(f"  - {var}" for var in missing_vars)
        )

    # Validate JWT secret key strength
    jwt_secret = os.getenv("JWT_SECRET_KEY", "")
    if len(jwt_secret) < 32:
        raise ValueError(
            "JWT_SECRET_KEY must be at least 32 characters long for security. "
            f"Current length: {len(jwt_secret)}"
        )

    # Validate database URL format
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url.startswith(("postgresql://", "postgres://")):
        raise ValueError(
            "DATABASE_URL must be a valid PostgreSQL connection string "
            "(starting with postgresql:// or postgres://)"
        )

    # Validate environment setting
    environment = os.getenv("ENVIRONMENT", "development")
    valid_environments = ["development", "staging", "production"]
    if environment not in valid_environments:
        raise ValueError(
            f"ENVIRONMENT must be one of {valid_environments}, got: {environment}"
        )

    # Production-specific validations
    if environment == "production":
        # Ensure CORS is properly configured
        cors_origins = os.getenv("CORS_ORIGINS", "")
        if not cors_origins or cors_origins == "*":
            raise ValueError(
                "CORS_ORIGINS must be explicitly set in production (no wildcards allowed)"
            )

        # Warn about missing optional but recommended vars
        if not os.getenv("REDIS_URL"):
            import logging
            logging.warning(
                "REDIS_URL not set. Caching will use in-memory storage which "
                "is not recommended for production with multiple instances."
            )


settings = Settings()