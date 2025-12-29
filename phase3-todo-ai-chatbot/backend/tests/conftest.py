"""Shared test fixtures for the test suite"""
import os
import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

# Set test environment variables before importing app
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("GROQ_API_KEY", "test_api_key_for_testing")
os.environ.setdefault("GROQ_MODEL", "llama-3.3-70b-versatile")
os.environ.setdefault("SECRET_KEY", "test_secret_key_12345678901234567890123456789012")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")


@pytest.fixture(name="session", scope="function")
def session_fixture():
    """Create a fresh database session for each test"""
    # Create a new engine for each test with in-memory database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Import all models to ensure they're registered
    from src.models.user import User
    from src.models.task import Task
    from src.models.conversation import Conversation
    from src.models.message import Message

    # Create all tables (checkfirst=True to avoid duplicate index errors)
    SQLModel.metadata.create_all(engine, checkfirst=True)

    with Session(engine) as session:
        yield session

    # Clean up
    engine.dispose()


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with database session override"""
    # Import app here to avoid early model registration
    from fastapi.testclient import TestClient
    from src.main import app
    from src.database import get_session

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_token(session: Session):
    """Create a test user and return auth token"""
    from src.models.user import User
    from src.auth.security import hash_password, create_access_token
    from uuid import uuid4

    user = User(
        id=uuid4(),
        email="test@example.com",
        name="Test User",
        password_hash=hash_password("testpassword123"),
        is_active=True
    )
    session.add(user)
    session.commit()

    token = create_access_token({"sub": str(user.id), "email": user.email})
    return token, user
