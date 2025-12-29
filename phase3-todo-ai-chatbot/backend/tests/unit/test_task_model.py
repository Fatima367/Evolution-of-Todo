"""Unit tests for Task model"""
import pytest
from datetime import datetime
from src.models.task import Task, TaskStatus, TaskPriority


def test_task_creation():
    """Test task model instantiation"""
    task = Task(
        title="Test Task",
        description="Test Description",
        status=TaskStatus.PENDING,
        priority=TaskPriority.HIGH,
        user_id="test-user-id"
    )
    
    assert task.title == "Test Task"
    assert task.description == "Test Description"
    assert task.status == TaskStatus.PENDING
    assert task.priority == TaskPriority.HIGH
    assert task.completed_at is None


def test_task_defaults():
    """Test task model defaults"""
    task = Task(title="Test Task", user_id="test-user-id")
    
    assert task.status == TaskStatus.PENDING
    assert task.priority == TaskPriority.MEDIUM
    assert task.description is None
    assert task.tags is None
