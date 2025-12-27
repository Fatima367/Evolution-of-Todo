"""Shared test fixtures for the test suite"""
import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from fastapi.testclient import TestClient
from src.main import app
from src.database import get_session
from src.auth.security import create_access_token


@pytest.fixture(name="session")
def session_fixture():
    """Create a fresh database session for each test"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with database session override"""
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
    from src.auth.security import hash_password
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
