"""Integration tests for task sorting functionality"""
import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from src.models.task import TaskPriority


def test_sort_tasks_by_due_date_ascending(client: TestClient, auth_token):
    """Test T001: Sort tasks by due_date in ascending order (earliest first)"""
    token, _ = auth_token

    # Create tasks with different due dates
    base_date = datetime.now(timezone.utc)
    client.post(
        "/tasks/",
        json={
            "title": "Task Due Next Week",
            "due_date": (base_date + timedelta(days=7)).isoformat()
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    client.post(
        "/tasks/",
        json={
            "title": "Task Due Tomorrow",
            "due_date": (base_date + timedelta(days=1)).isoformat()
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    client.post(
        "/tasks/",
        json={
            "title": "Task Due Today",
            "due_date": (base_date + timedelta(hours=12)).isoformat()
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    # Sort by due_date ascending
    response = client.get(
        "/tasks/?sort_by=due_date&sort_order=asc",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    tasks = data["tasks"]

    # Verify order: due_date ascending (earliest first)
    assert len(tasks) >= 3
    for i in range(len(tasks) - 1):
        if tasks[i]["due_date"] and tasks[i+1]["due_date"]:
            assert tasks[i]["due_date"] <= tasks[i+1]["due_date"]


def test_sort_tasks_by_priority_ascending(client: TestClient, auth_token):
    """Test T002: Sort tasks by priority in ascending order (low to urgent)"""
    token, _ = auth_token

    # Create tasks with different priorities
    client.post(
        "/tasks/",
        json={"title": "High Priority Task", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"}
    )
    client.post(
        "/tasks/",
        json={"title": "Low Priority Task", "priority": "low"},
        headers={"Authorization": f"Bearer {token}"}
    )
    client.post(
        "/tasks/",
        json={"title": "Urgent Priority Task", "priority": "urgent"},
        headers={"Authorization": f"Bearer {token}"}
    )
    client.post(
        "/tasks/",
        json={"title": "Medium Priority Task", "priority": "medium"},
        headers={"Authorization": f"Bearer {token}"}
    )

    # Sort by priority ascending
    response = client.get(
        "/tasks/?sort_by=priority&sort_order=asc",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    tasks = data["tasks"]

    # Verify order: low, medium, high, urgent (enum value order)
    priority_order = {"low": 0, "medium": 1, "high": 2, "urgent": 3}
    priorities = [task["priority"] for task in tasks]

    for i in range(len(priorities) - 1):
        assert priority_order[priorities[i]] <= priority_order[priorities[i+1]]


def test_sort_tasks_by_title_alphabetical(client: TestClient, auth_token):
    """Test T003: Sort tasks alphabetically by title"""
    token, _ = auth_token

    # Create tasks with different titles
    client.post(
        "/tasks/",
        json={"title": "Zebra Task"},
        headers={"Authorization": f"Bearer {token}"}
    )
    client.post(
        "/tasks/",
        json={"title": "Apple Task"},
        headers={"Authorization": f"Bearer {token}"}
    )
    client.post(
        "/tasks/",
        json={"title": "Mango Task"},
        headers={"Authorization": f"Bearer {token}"}
    )

    # Sort by title ascending (A-Z)
    response = client.get(
        "/tasks/?sort_by=title&sort_order=asc",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    tasks = data["tasks"]

    # Verify alphabetical order
    assert len(tasks) >= 3
    titles = [task["title"] for task in tasks]
    assert titles == sorted(titles)


def test_sort_direction_toggle(client: TestClient, auth_token):
    """Test T004: Sort direction toggle between ascending and descending"""
    token, _ = auth_token

    # Create tasks
    client.post(
        "/tasks/",
        json={"title": "C Task"},
        headers={"Authorization": f"Bearer {token}"}
    )
    client.post(
        "/tasks/",
        json={"title": "A Task"},
        headers={"Authorization": f"Bearer {token}"}
    )
    client.post(
        "/tasks/",
        json={"title": "B Task"},
        headers={"Authorization": f"Bearer {token}"}
    )

    # Sort ascending (A-Z)
    response_asc = client.get(
        "/tasks/?sort_by=title&sort_order=asc",
        headers={"Authorization": f"Bearer {token}"}
    )
    tasks_asc = response_asc.json()["tasks"]
    titles_asc = [task["title"] for task in tasks_asc]

    # Sort descending (Z-A)
    response_desc = client.get(
        "/tasks/?sort_by=title&sort_order=desc",
        headers={"Authorization": f"Bearer {token}"}
    )
    tasks_desc = response_desc.json()["tasks"]
    titles_desc = [task["title"] for task in tasks_desc]

    # Verify opposite order
    assert titles_asc == sorted(titles_asc)
    assert titles_desc == sorted(titles_desc, reverse=True)
    assert titles_asc == list(reversed(titles_desc))


def test_sort_with_null_due_dates(client: TestClient, auth_token):
    """Test T005: Sort tasks with NULL due_date values"""
    token, _ = auth_token

    base_date = datetime.now(timezone.utc)

    # Create tasks with and without due dates
    client.post(
        "/tasks/",
        json={"title": "Task with due date", "due_date": (base_date + timedelta(days=1)).isoformat()},
        headers={"Authorization": f"Bearer {token}"}
    )
    client.post(
        "/tasks/",
        json={"title": "Task without due date"},
        headers={"Authorization": f"Bearer {token}"}
    )
    client.post(
        "/tasks/",
        json={"title": "Another task with due date", "due_date": (base_date + timedelta(days=2)).isoformat()},
        headers={"Authorization": f"Bearer {token}"}
    )

    # Sort by due_date ascending
    response = client.get(
        "/tasks/?sort_by=due_date&sort_order=asc",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    tasks = data["tasks"]

    # Verify NULL values come last in ascending order
    assert len(tasks) >= 3
    # Tasks with due dates should come before tasks without due dates
    tasks_with_dates = [t for t in tasks if t["due_date"] is not None]
    tasks_without_dates = [t for t in tasks if t["due_date"] is None]

    # All tasks with dates should be before tasks without dates
    for task_with_date in tasks_with_dates:
        for task_without_date in tasks_without_dates:
            with_date_index = tasks.index(task_with_date)
            without_date_index = tasks.index(task_without_date)
            assert with_date_index < without_date_index


def test_sort_combined_with_filters(client: TestClient, auth_token):
    """Test T006: Sort combined with existing filters"""
    token, _ = auth_token

    base_date = datetime.now(timezone.utc)

    # Create tasks with various due dates
    task1 = client.post(
        "/tasks/",
        json={
            "title": "Completed Task Due Soon",
            "due_date": (base_date + timedelta(days=1)).isoformat()
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    task1_id = task1.json()["id"]

    task2 = client.post(
        "/tasks/",
        json={
            "title": "Completed Task Due Later",
            "due_date": (base_date + timedelta(days=7)).isoformat()
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    task2_id = task2.json()["id"]

    client.post(
        "/tasks/",
        json={
            "title": "Pending Task Due Soon",
            "due_date": (base_date + timedelta(days=2)).isoformat()
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    # Update first two tasks to completed status
    client.put(
        f"/tasks/{task1_id}",
        json={"status": "completed"},
        headers={"Authorization": f"Bearer {token}"}
    )
    client.put(
        f"/tasks/{task2_id}",
        json={"status": "completed"},
        headers={"Authorization": f"Bearer {token}"}
    )

    # Filter by completed status and sort by due_date ascending
    response = client.get(
        "/tasks/?status=completed&sort_by=due_date&sort_order=asc",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    tasks = data["tasks"]

    # Verify only completed tasks are returned
    assert all(task["status"] == "completed" for task in tasks)
    assert len(tasks) == 2

    # Verify sorted by due_date
    if tasks[0]["due_date"] and tasks[1]["due_date"]:
        assert tasks[0]["due_date"] <= tasks[1]["due_date"]


def test_sort_default_behavior(client: TestClient, auth_token):
    """Test default sorting behavior (created_at desc)"""
    token, _ = auth_token

    # Create tasks in order
    task1 = client.post(
        "/tasks/",
        json={"title": "First Task"},
        headers={"Authorization": f"Bearer {token}"}
    )
    import time
    time.sleep(0.01)  # Small delay to ensure different timestamps

    task2 = client.post(
        "/tasks/",
        json={"title": "Second Task"},
        headers={"Authorization": f"Bearer {token}"}
    )
    time.sleep(0.01)

    task3 = client.post(
        "/tasks/",
        json={"title": "Third Task"},
        headers={"Authorization": f"Bearer {token}"}
    )

    # Get tasks without sort parameters (default)
    response = client.get(
        "/tasks/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    tasks = data["tasks"]

    # Verify default order: created_at descending (newest first)
    assert len(tasks) >= 3
    assert tasks[0]["title"] == "Third Task"
    assert tasks[1]["title"] == "Second Task"
    assert tasks[2]["title"] == "First Task"


def test_invalid_sort_by_parameter(client: TestClient, auth_token):
    """Test that invalid sort_by parameter returns 422 validation error"""
    token, _ = auth_token

    response = client.get(
        "/tasks/?sort_by=invalid_field",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 422


def test_invalid_sort_order_parameter(client: TestClient, auth_token):
    """Test that invalid sort_order parameter returns 422 validation error"""
    token, _ = auth_token

    response = client.get(
        "/tasks/?sort_by=due_date&sort_order=invalid",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 422
