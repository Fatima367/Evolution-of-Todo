"""Database connection and session management for Neon Serverless PostgreSQL"""
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.pool import NullPool
from src.config import settings


# Neon Serverless requires NullPool for connection management
engine = create_engine(
    settings.database_url,
    echo=settings.environment == "development",
    poolclass=NullPool,
    connect_args={"sslmode": "require"} if "neon.tech" in settings.database_url else {}
)


def create_db_and_tables():
    """Create all database tables"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency for database session

    Yields:
        Session: SQLModel session for database operations
    """
    with Session(engine) as session:
        yield session
