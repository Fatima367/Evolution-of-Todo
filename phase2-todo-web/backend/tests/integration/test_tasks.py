"""Integration tests for task endpoints"""
import pytest
from fastapi.testclient import TestClient


def test_create_task(client: TestClient, auth_token):
    """Test task creation"""
    token, _ = auth_token
    
    response = client.post(
        "/tasks/",
        json={
            "title": "Test Task",
            "description": "Test Description",
            "priority": "high"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["priority"] == "high"


def test_get_tasks(client: TestClient, auth_token):
    """Test getting user's tasks"""
    token, _ = auth_token
    
    # Create a task first
    client.post(
        "/tasks/",
        json={"title": "Test Task"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Get tasks
    response = client.get(
        "/tasks/",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert len(data["tasks"]) >= 1


def test_data_isolation(client: TestClient, auth_token, session):
    """Test that users can only see their own tasks"""
    token1, user1 = auth_token
    
    # Create task for user1
    response1 = client.post(
        "/tasks/",
        json={"title": "User1 Task"},
        headers={"Authorization": f"Bearer {token1}"}
    )
    task1_id = response1.json()["id"]
    
    # Create second user and token
    from src.models.user import User
    from src.auth.security import hash_password, create_access_token
    from uuid import uuid4
    
    user2 = User(
        id=uuid4(),
        email="user2@example.com",
        name="User 2",
        password_hash=hash_password("password123"),
        is_active=True
    )
    session.add(user2)
    session.commit()
    token2 = create_access_token({"sub": str(user2.id), "email": user2.email})
    
    # Try to access user1's task as user2
    response = client.get(
        f"/tasks/{task1_id}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    
    assert response.status_code == 404  # Should not find the task
