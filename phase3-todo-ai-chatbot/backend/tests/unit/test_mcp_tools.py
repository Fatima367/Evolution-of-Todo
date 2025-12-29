"""Unit tests for MCP tools

These tests verify the task management tools exposed to the AI agent
via the OpenAI Agents SDK.

Test Coverage:
- T032: add_task tool returns task_id and "created" status
- T033: list_tasks tool filters by status
- T034: complete_task tool updates task status
- T035: delete_task tool removes task
- T036: update_task tool modifies task fields
"""
import pytest
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
    """Test that create_task_tools returns all 5 tools"""
    tools = create_task_tools(session, str(test_user.id))
    assert len(tools) == 5
    tool_names = [tool.name for tool in tools]
    assert "add_task" in tool_names
    assert "list_tasks" in tool_names
    assert "complete_task" in tool_names
    assert "delete_task" in tool_names
    assert "update_task" in tool_names


def test_add_task_returns_task_id_and_created_status(task_tools, session: Session, test_user: User):
    """T032: Test add_task tool returns task_id and 'created' status"""
    # Find add_task tool
    add_task = next(tool for tool in task_tools if tool.name == "add_task")

    # Execute tool
    result = add_task.func(
        title="Test Task",
        description="Test Description",
        priority="high"
    )

    # Verify return format
    assert "task_id" in result
    assert "status" in result
    assert "title" in result
    assert "priority" in result

    assert result["status"] == "created"
    assert result["title"] == "Test Task"
    assert result["priority"] == "high"

    # Verify task was created in database
    task_id = result["task_id"]
    task = session.get(Task, task_id)
    assert task is not None
    assert task.title == "Test Task"
    assert task.description == "Test Description"
    assert task.priority == TaskPriority.HIGH
    assert task.status == TaskStatus.PENDING
    assert task.user_id == test_user.id


def test_add_task_with_minimal_params(task_tools, session: Session, test_user: User):
    """Test add_task with only required title parameter"""
    add_task = next(tool for tool in task_tools if tool.name == "add_task")

    result = add_task.func(title="Minimal Task")

    assert result["status"] == "created"
    assert result["title"] == "Minimal Task"
    assert result["priority"] == "medium"  # Default priority

    # Verify in database
    task = session.get(Task, result["task_id"])
    assert task.description is None
    assert task.priority == TaskPriority.MEDIUM


def test_add_task_invalid_priority_defaults_to_medium(task_tools, session: Session):
    """Test add_task with invalid priority defaults to medium"""
    add_task = next(tool for tool in task_tools if tool.name == "add_task")

    result = add_task.func(title="Task", priority="invalid")

    assert result["priority"] == "medium"
    task = session.get(Task, result["task_id"])
    assert task.priority == TaskPriority.MEDIUM


def test_list_tasks_filters_by_status_all(task_tools, session: Session, test_user: User):
    """T033: Test list_tasks tool filters by status - all"""
    # Create tasks with different statuses
    add_task = next(tool for tool in task_tools if tool.name == "add_task")
    list_tasks = next(tool for tool in task_tools if tool.name == "list_tasks")

    add_task.func(title="Pending Task")
    task2 = add_task.func(title="In Progress Task")
    task3 = add_task.func(title="Completed Task")

    # Update statuses directly in DB
    t2 = session.get(Task, task2["task_id"])
    t2.status = TaskStatus.IN_PROGRESS
    t3 = session.get(Task, task3["task_id"])
    t3.status = TaskStatus.COMPLETED
    session.commit()

    # List all tasks
    result = list_tasks.func(status="all")

    assert "tasks" in result
    assert "count" in result
    assert result["count"] == 3
    assert len(result["tasks"]) == 3


def test_list_tasks_filters_by_status_pending(task_tools, session: Session):
    """T033: Test list_tasks tool filters by status - pending"""
    add_task = next(tool for tool in task_tools if tool.name == "add_task")
    list_tasks = next(tool for tool in task_tools if tool.name == "list_tasks")

    # Create tasks
    add_task.func(title="Pending Task 1")
    add_task.func(title="Pending Task 2")
    task3 = add_task.func(title="Completed Task")

    # Mark one as completed
    t3 = session.get(Task, task3["task_id"])
    t3.status = TaskStatus.COMPLETED
    session.commit()

    # List only pending
    result = list_tasks.func(status="pending")

    assert result["count"] == 2
    for task in result["tasks"]:
        assert task["status"] == "pending"


def test_list_tasks_filters_by_status_in_progress(task_tools, session: Session):
    """T033: Test list_tasks tool filters by status - in_progress"""
    add_task = next(tool for tool in task_tools if tool.name == "add_task")
    list_tasks = next(tool for tool in task_tools if tool.name == "list_tasks")

    task1 = add_task.func(title="Task 1")
    task2 = add_task.func(title="Task 2")

    # Mark as in progress
    t1 = session.get(Task, task1["task_id"])
    t1.status = TaskStatus.IN_PROGRESS
    session.commit()

    result = list_tasks.func(status="in_progress")

    assert result["count"] == 1
    assert result["tasks"][0]["status"] == "in_progress"


def test_list_tasks_filters_by_status_completed(task_tools, session: Session):
    """T033: Test list_tasks tool filters by status - completed"""
    add_task = next(tool for tool in task_tools if tool.name == "add_task")
    list_tasks = next(tool for tool in task_tools if tool.name == "list_tasks")

    task1 = add_task.func(title="Task 1")
    task2 = add_task.func(title="Task 2")

    # Mark one as completed
    t1 = session.get(Task, task1["task_id"])
    t1.status = TaskStatus.COMPLETED
    t1.completed_at = datetime.utcnow()
    session.commit()

    result = list_tasks.func(status="completed")

    assert result["count"] == 1
    assert result["tasks"][0]["status"] == "completed"


def test_list_tasks_respects_limit(task_tools, session: Session):
    """Test list_tasks respects limit parameter"""
    add_task = next(tool for tool in task_tools if tool.name == "add_task")
    list_tasks = next(tool for tool in task_tools if tool.name == "list_tasks")

    # Create 5 tasks
    for i in range(5):
        add_task.func(title=f"Task {i}")

    # List with limit=2
    result = list_tasks.func(limit=2)

    assert result["count"] == 2
    assert len(result["tasks"]) == 2


def test_list_tasks_returns_task_details(task_tools, session: Session):
    """Test list_tasks returns all task details"""
    add_task = next(tool for tool in task_tools if tool.name == "add_task")
    list_tasks = next(tool for tool in task_tools if tool.name == "list_tasks")

    add_task.func(title="Detailed Task", description="Description", priority="urgent")

    result = list_tasks.func()

    task = result["tasks"][0]
    assert "id" in task
    assert "title" in task
    assert "description" in task
    assert "status" in task
    assert "priority" in task
    assert "due_date" in task
    assert "created_at" in task

    assert task["title"] == "Detailed Task"
    assert task["description"] == "Description"
    assert task["priority"] == "urgent"


def test_complete_task_updates_status(task_tools, session: Session):
    """T034: Test complete_task tool updates task status"""
    add_task = next(tool for tool in task_tools if tool.name == "add_task")
    complete_task = next(tool for tool in task_tools if tool.name == "complete_task")

    # Create task
    task_result = add_task.func(title="Task to Complete")
    task_id = task_result["task_id"]

    # Complete it
    result = complete_task.func(task_id=task_id)

    assert result["task_id"] == task_id
    assert result["status"] == "completed"
    assert result["title"] == "Task to Complete"

    # Verify in database
    task = session.get(Task, task_id)
    assert task.status == TaskStatus.COMPLETED
    assert task.completed_at is not None
    assert task.updated_at is not None


def test_complete_task_with_invalid_id(task_tools):
    """Test complete_task with invalid task ID format"""
    complete_task = next(tool for tool in task_tools if tool.name == "complete_task")

    result = complete_task.func(task_id="invalid-id")

    assert "error" in result
    assert result["status"] == "error"
    assert "Invalid task ID format" in result["error"]


def test_complete_task_not_found(task_tools):
    """Test complete_task with non-existent task ID"""
    complete_task = next(tool for tool in task_tools if tool.name == "complete_task")

    fake_id = str(uuid4())
    result = complete_task.func(task_id=fake_id)

    assert "error" in result
    assert result["status"] == "error"
    assert "Task not found" in result["error"]


def test_delete_task_removes_task(task_tools, session: Session):
    """T035: Test delete_task tool removes task"""
    add_task = next(tool for tool in task_tools if tool.name == "add_task")
    delete_task = next(tool for tool in task_tools if tool.name == "delete_task")

    # Create task
    task_result = add_task.func(title="Task to Delete")
    task_id = task_result["task_id"]

    # Verify it exists
    task = session.get(Task, task_id)
    assert task is not None

    # Delete it
    result = delete_task.func(task_id=task_id)

    assert result["task_id"] == task_id
    assert result["status"] == "deleted"
    assert result["title"] == "Task to Delete"

    # Verify it's gone
    session.expire_all()  # Clear session cache
    task = session.get(Task, task_id)
    assert task is None


def test_delete_task_with_invalid_id(task_tools):
    """Test delete_task with invalid task ID format"""
    delete_task = next(tool for tool in task_tools if tool.name == "delete_task")

    result = delete_task.func(task_id="invalid-id")

    assert "error" in result
    assert result["status"] == "error"


def test_delete_task_not_found(task_tools):
    """Test delete_task with non-existent task ID"""
    delete_task = next(tool for tool in task_tools if tool.name == "delete_task")

    fake_id = str(uuid4())
    result = delete_task.func(task_id=fake_id)

    assert "error" in result
    assert result["status"] == "error"


def test_update_task_modifies_title(task_tools, session: Session):
    """T036: Test update_task tool modifies task title"""
    add_task = next(tool for tool in task_tools if tool.name == "add_task")
    update_task = next(tool for tool in task_tools if tool.name == "update_task")

    # Create task
    task_result = add_task.func(title="Original Title")
    task_id = task_result["task_id"]

    # Update title
    result = update_task.func(task_id=task_id, title="Updated Title")

    assert result["status"] == "updated"
    assert result["title"] == "Updated Title"

    # Verify in database
    task = session.get(Task, task_id)
    assert task.title == "Updated Title"


def test_update_task_modifies_description(task_tools, session: Session):
    """T036: Test update_task tool modifies task description"""
    add_task = next(tool for tool in task_tools if tool.name == "add_task")
    update_task = next(tool for tool in task_tools if tool.name == "update_task")

    task_result = add_task.func(title="Task", description="Old Desc")
    task_id = task_result["task_id"]

    update_task.func(task_id=task_id, description="New Desc")

    task = session.get(Task, task_id)
    assert task.description == "New Desc"


def test_update_task_modifies_priority(task_tools, session: Session):
    """T036: Test update_task tool modifies task priority"""
    add_task = next(tool for tool in task_tools if tool.name == "add_task")
    update_task = next(tool for tool in task_tools if tool.name == "update_task")

    task_result = add_task.func(title="Task", priority="low")
    task_id = task_result["task_id"]

    result = update_task.func(task_id=task_id, priority="urgent")

    assert result["priority"] == "urgent"
    task = session.get(Task, task_id)
    assert task.priority == TaskPriority.URGENT


def test_update_task_modifies_status(task_tools, session: Session):
    """T036: Test update_task tool modifies task status"""
    add_task = next(tool for tool in task_tools if tool.name == "add_task")
    update_task = next(tool for tool in task_tools if tool.name == "update_task")

    task_result = add_task.func(title="Task")
    task_id = task_result["task_id"]

    result = update_task.func(task_id=task_id, status="in_progress")

    assert result["task_status"] == "in_progress"
    task = session.get(Task, task_id)
    assert task.status == TaskStatus.IN_PROGRESS


def test_update_task_status_to_completed_sets_completed_at(task_tools, session: Session):
    """Test update_task sets completed_at when status becomes completed"""
    add_task = next(tool for tool in task_tools if tool.name == "add_task")
    update_task = next(tool for tool in task_tools if tool.name == "update_task")

    task_result = add_task.func(title="Task")
    task_id = task_result["task_id"]

    update_task.func(task_id=task_id, status="completed")

    task = session.get(Task, task_id)
    assert task.status == TaskStatus.COMPLETED
    assert task.completed_at is not None


def test_update_task_status_from_completed_clears_completed_at(task_tools, session: Session):
    """Test update_task clears completed_at when status changes from completed"""
    add_task = next(tool for tool in task_tools if tool.name == "add_task")
    update_task = next(tool for tool in task_tools if tool.name == "update_task")

    task_result = add_task.func(title="Task")
    task_id = task_result["task_id"]

    # Complete then reopen
    update_task.func(task_id=task_id, status="completed")
    update_task.func(task_id=task_id, status="pending")

    task = session.get(Task, task_id)
    assert task.status == TaskStatus.PENDING
    assert task.completed_at is None


def test_update_task_multiple_fields(task_tools, session: Session):
    """T036: Test update_task tool modifies multiple fields at once"""
    add_task = next(tool for tool in task_tools if tool.name == "add_task")
    update_task = next(tool for tool in task_tools if tool.name == "update_task")

    task_result = add_task.func(title="Original", description="Old", priority="low")
    task_id = task_result["task_id"]

    result = update_task.func(
        task_id=task_id,
        title="Updated Title",
        description="New Description",
        priority="high",
        status="in_progress"
    )

    assert result["status"] == "updated"
    assert result["title"] == "Updated Title"
    assert result["priority"] == "high"
    assert result["task_status"] == "in_progress"

    task = session.get(Task, task_id)
    assert task.title == "Updated Title"
    assert task.description == "New Description"
    assert task.priority == TaskPriority.HIGH
    assert task.status == TaskStatus.IN_PROGRESS


def test_update_task_with_invalid_id(task_tools):
    """Test update_task with invalid task ID format"""
    update_task = next(tool for tool in task_tools if tool.name == "update_task")

    result = update_task.func(task_id="invalid-id", title="Title")

    assert "error" in result
    assert result["status"] == "error"


def test_update_task_not_found(task_tools):
    """Test update_task with non-existent task ID"""
    update_task = next(tool for tool in task_tools if tool.name == "update_task")

    fake_id = str(uuid4())
    result = update_task.func(task_id=fake_id, title="Title")

    assert "error" in result
    assert result["status"] == "error"


def test_update_task_ignores_invalid_priority(task_tools, session: Session):
    """Test update_task ignores invalid priority values"""
    add_task = next(tool for tool in task_tools if tool.name == "add_task")
    update_task = next(tool for tool in task_tools if tool.name == "update_task")

    task_result = add_task.func(title="Task", priority="high")
    task_id = task_result["task_id"]

    update_task.func(task_id=task_id, priority="invalid")

    # Priority should remain unchanged
    task = session.get(Task, task_id)
    assert task.priority == TaskPriority.HIGH


def test_update_task_ignores_invalid_status(task_tools, session: Session):
    """Test update_task ignores invalid status values"""
    add_task = next(tool for tool in task_tools if tool.name == "add_task")
    update_task = next(tool for tool in task_tools if tool.name == "update_task")

    task_result = add_task.func(title="Task")
    task_id = task_result["task_id"]

    update_task.func(task_id=task_id, status="invalid")

    # Status should remain unchanged
    task = session.get(Task, task_id)
    assert task.status == TaskStatus.PENDING


def test_tools_enforce_user_isolation(session: Session):
    """Test that tools only access tasks belonging to the specified user"""
    # Create two users
    user1 = User(
        id=uuid4(),
        email="user1@example.com",
        name="User 1",
        password_hash=hash_password("pass"),
        is_active=True
    )
    user2 = User(
        id=uuid4(),
        email="user2@example.com",
        name="User 2",
        password_hash=hash_password("pass"),
        is_active=True
    )
    session.add(user1)
    session.add(user2)
    session.commit()

    # Create tools for user1
    user1_tools = create_task_tools(session, str(user1.id))
    add_task1 = next(tool for tool in user1_tools if tool.name == "add_task")
    list_tasks1 = next(tool for tool in user1_tools if tool.name == "list_tasks")

    # Create tools for user2
    user2_tools = create_task_tools(session, str(user2.id))
    list_tasks2 = next(tool for tool in user2_tools if tool.name == "list_tasks")
    complete_task2 = next(tool for tool in user2_tools if tool.name == "complete_task")

    # User1 creates a task
    task_result = add_task1.func(title="User1 Task")
    task_id = task_result["task_id"]

    # User1 can see their task
    result1 = list_tasks1.func()
    assert result1["count"] == 1

    # User2 cannot see user1's task
    result2 = list_tasks2.func()
    assert result2["count"] == 0

    # User2 cannot complete user1's task
    result_complete = complete_task2.func(task_id=task_id)
    assert "error" in result_complete
    assert result_complete["status"] == "error"
