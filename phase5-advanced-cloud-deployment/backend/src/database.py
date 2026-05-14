"""Database connection and session management for Neon Serverless PostgreSQL"""
import os
import time
from typing import Generator
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy import text
from sqlalchemy.pool import NullPool, QueuePool
from sqlalchemy.exc import OperationalError, DBAPIError
from src.config import settings
from src.lib.logging import get_logger

logger = get_logger(__name__)

# Database connection pooling configuration
# For production cloud deployment, use connection pooling for better performance
# For serverless/local development, use NullPool to avoid connection exhaustion
USE_CONNECTION_POOLING = os.getenv("DB_USE_POOLING", "false").lower() == "true"

# Connection pool settings (only used when USE_CONNECTION_POOLING=true)
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))
POOL_PRE_PING = os.getenv("DB_POOL_PRE_PING", "true").lower() == "true"

# Retry configuration
MAX_RETRIES = int(os.getenv("DB_MAX_RETRIES", "3"))
RETRY_DELAY = float(os.getenv("DB_RETRY_DELAY", "1.0"))  # seconds
RETRY_BACKOFF = float(os.getenv("DB_RETRY_BACKOFF", "2.0"))  # exponential backoff multiplier


engine = None


def create_engine_with_retry(max_retries: int = MAX_RETRIES) -> any:
    """
    Create database engine with retry logic

    Args:
        max_retries: Maximum number of connection attempts

    Returns:
        SQLAlchemy engine

    Raises:
        OperationalError: If connection fails after all retries
    """
    last_error = None
    delay = RETRY_DELAY

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Attempting to connect to database (attempt {attempt}/{max_retries})")

            # Configure engine based on environment
            if USE_CONNECTION_POOLING:
                # Production cloud deployment with connection pooling
                db_engine = create_engine(
                    settings.database_url,
                    echo=settings.environment == "development",
                    poolclass=QueuePool,
                    pool_size=POOL_SIZE,
                    max_overflow=MAX_OVERFLOW,
                    pool_timeout=POOL_TIMEOUT,
                    pool_recycle=POOL_RECYCLE,
                    pool_pre_ping=POOL_PRE_PING,
                    connect_args={"sslmode": "require"} if "neon.tech" in settings.database_url else {}
                )
            else:
                # Neon Serverless or local development - use NullPool
                db_engine = create_engine(
                    settings.database_url,
                    echo=settings.environment == "development",
                    poolclass=NullPool,
                    connect_args={"sslmode": "require"} if "neon.tech" in settings.database_url else {}
                )

            # Test connection
            with db_engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            logger.info("Database connection established successfully")
            return db_engine

        except (OperationalError, DBAPIError) as e:
            last_error = e
            logger.warning(
                f"Database connection attempt {attempt}/{max_retries} failed: {e}",
                extra={"attempt": attempt, "max_retries": max_retries}
            )

            if attempt < max_retries:
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= RETRY_BACKOFF  # Exponential backoff
            else:
                logger.error(
                    f"Failed to connect to database after {max_retries} attempts",
                    exc_info=True
                )

    # All retries exhausted
    raise OperationalError(
        f"Failed to connect to database after {max_retries} attempts",
        params=None,
        orig=last_error
    )


def initialize_database():
    """Create database engine and tables"""
    global engine
    engine = create_engine_with_retry()
    logger.info("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created successfully.")


def get_session() -> Generator[Session, None, None]:
    """Dependency for database session

    Yields:
        Session: SQLModel session for database operations
    """
    if engine is None:
        raise RuntimeError("Database not initialized. Call initialize_database() first.")
    with Session(engine) as session:
        yield session
