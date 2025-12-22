"""Integration tests for authentication endpoints"""
import pytest
from fastapi.testclient import TestClient


def test_register_user(client: TestClient):
    """Test user registration"""
    response = client.post(
        "/auth/register",
        json={
            "email": "newuser@example.com",
            "name": "New User",
            "password": "securepassword123"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "newuser@example.com"


def test_login_user(client: TestClient, auth_token):
    """Test user login"""
    _, user = auth_token
    
    response = client.post(
        "/auth/login",
        json={
            "email": user.email,
            "password": "testpassword123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == user.email


def test_get_current_user(client: TestClient, auth_token):
    """Test getting current user info"""
    token, user = auth_token
    
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user.email
    assert data["name"] == user.name
