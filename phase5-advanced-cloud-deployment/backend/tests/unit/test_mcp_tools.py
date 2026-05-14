"""Unit tests for MCP tools

These tests verify the task management tools exposed to the AI agent
via the OpenAI Agents SDK.
"""
import pytest
import uuid
from uuid import uuid4
from sqlmodel import Session, select
from datetime import datetime

from src.models.task import Task, TaskStatus, TaskPriority
from src.models.user import User
from src.auth.security import hash_password
from src.todo_chatkit.tools import create_task_tools


@pytest.fixture
def test_user(session: Session):
    """Create a test user for tool testing"""
    user = User(
        id=uuid4(),
        email="tooltest@example.com",
        name="Tool Test User",
        password_hash=hash_password("testpassword123"),
        is_active=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def task_tools(session: Session, test_user: User):
    """Create task tools for the test user"""
    return create_task_tools(session, str(test_user.id))


def test_create_task_tools_returns_correct_count(session: Session, test_user: User):
    """Test that create_task_tools returns all 8 tools"""
    tools = create_task_tools(session, str(test_user.id))
    assert len(tools) == 8
    tool_names = [tool.name for tool in tools]
    assert "add_task" in tool_names
    assert "list_tasks" in tool_names
    assert "complete_task" in tool_names
    assert "delete_task" in tool_names
    assert "update_task" in tool_names
    assert "bulk_complete" in tool_names
    assert "bulk_delete" in tool_names
    assert "clear_all" in tool_names


def test_bulk_operations_names(task_tools):
    """T074: Test bulk operations tools are correctly named"""
    bulk_complete = next(tool for tool in task_tools if tool.name == "bulk_complete")
    bulk_delete = next(tool for tool in task_tools if tool.name == "bulk_delete")
    clear_all = next(tool for tool in task_tools if tool.name == "clear_all")

    assert bulk_complete.name == "bulk_complete"
    assert bulk_delete.name == "bulk_delete"
    assert clear_all.name == "clear_all"
