"""Database connection and session management for Neon Serverless PostgreSQL"""
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.pool import NullPool
from src.config import settings

engine = None

def initialize_database():
    """Create database engine and tables"""
    global engine
    engine = create_engine(
        settings.database_url,
        echo=settings.environment == "development",
        poolclass=NullPool,
        connect_args={"sslmode": "require"} if "neon.tech" in settings.database_url else {}
    )
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency for database session

    Yields:
        Session: SQLModel session for database operations
    """
    if engine is None:
        raise RuntimeError("Database not initialized. Call initialize_database() first.")
    with Session(engine) as session:
        yield session
