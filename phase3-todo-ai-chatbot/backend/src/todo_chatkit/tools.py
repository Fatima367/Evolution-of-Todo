"""MCP tools for task management operations

These tools are exposed to the AI agent via OpenAI Agents SDK,
allowing natural language task management.
"""
import uuid
from datetime import datetime
from typing import Any, Optional, Dict, List, Annotated

from dateutil import parser
from pydantic import Field

from sqlmodel import Session, select
from agents import function_tool, RunContextWrapper

from src.models.task import Task, TaskStatus, TaskPriority
from src.models.user import User
from src.services.task_service import TaskService
from src.schemas.task_schemas import TaskCreate, TaskUpdate


class TaskToolContext:
    """Context passed to tools containing session, user_id and thread info

    This context is passed via RunContextWrapper when running the agent.
    """
    session: Session
    user_id: str  # UUID as string
    thread_id: str

    def __init__(self, session: Session, user_id: str, thread_id: str = ""):
        self.session = session
        self.user_id = user_id
        self.thread_id = thread_id


def get_tool_context(ctx: Any) -> tuple[Optional[Session], Optional[str]]:
    """Extract session and user_id from various possible context structures"""
    # Get raw context (handle RunContextWrapper or direct object)
    raw_ctx = ctx.context if hasattr(ctx, 'context') else ctx

    # Try direct attributes (matches TaskToolContext or direct mock)
    session = getattr(raw_ctx, 'session', None)
    user_id = getattr(raw_ctx, 'user_id', None)

    # Try request_context (matches ChatKit AgentContext)
    if session is None and hasattr(raw_ctx, 'request_context'):
        req_ctx = getattr(raw_ctx, 'request_context', None)
        if req_ctx:
            session = getattr(req_ctx, 'session', session)
            user_id = getattr(req_ctx, 'user_id', user_id)

    return session, user_id


def _resolve_and_validate_task(
    session_obj: Session,
    task_id: str,
    mock_user: User
) -> tuple[Optional[Task], Optional[Dict[str, Any]]]:
    """Find and validate a single task by ID or title. Returns (task, error_response)."""
    try:
        tasks = TaskService.find_tasks_by_query(session_obj, task_id, mock_user)
        if not tasks:
            return None, {"status": "error", "error": f"Task not found matching: {task_id}"}
        if len(tasks) > 1:
            return None, {
                "status": "ambiguous",
                "message": f"Multiple tasks found matching '{task_id}'. Please be more specific.",
                "matches": [{"id": str(t.id), "title": t.title, "status": t.status.value} for t in tasks]
            }
        return tasks[0], None
    except Exception as e:
        return None, {"status": "error", "error": str(e)}


def _build_task_tools(session: Session, user_id: str, thread_id: str) -> list[Any]:
    """Build all task tool functions with shared session/user context."""

    def _get_context(ctx: Any) -> tuple[Session, str]:
        session_obj, uid = get_tool_context(ctx)
        if not session_obj or not uid:
            return session, user_id
        return session_obj, uid

    @function_tool(name_override="add_task")
    def add_task(
        ctx: RunContextWrapper[Any],
        title: Annotated[str, Field(description="The title of the task")],
        description: Annotated[Optional[str], Field(default=None, description="The description of the task. If not provided by the user, use None.")] = None,
        priority: Annotated[Optional[str], Field(default=None, description="The priority of the task. Can be 'low', 'medium', 'high', or 'urgent'. If not provided by the user, use None.")] = None,
        due_date: Annotated[Optional[str], Field(default=None, description="The due date of the task. Accepts ISO format (e.g., '2024-12-31', '2024-12-31T23:59:59') or natural language (e.g., 'tomorrow', 'next monday', 'in 3 days'). If not provided by the user, use None.")] = None,
        tags: Annotated[Optional[List[str]], Field(default=None, description="A list of tags for the task (max 10 tags, each max 50 characters).")] = None
    ) -> Dict[str, Any]:
        """Create a new task with a title and optional description, priority, due date, and tags."""
        session_obj, uid = _get_context(ctx)
        mock_user = User(id=uuid.UUID(uid))

        prio = priority or "medium"
        try:
            priority_enum = TaskPriority(prio.lower())
        except ValueError:
            priority_enum = TaskPriority.MEDIUM
        
        due_date_obj = None
        if due_date:
            try:
                due_date_obj = parser.parse(due_date)
            except (ValueError, TypeError) as e:
                # Return error for invalid date format
                return {
                    "status": "error",
                    "error": f"Invalid date format: {str(e)}. Please use ISO format (e.g., '2024-12-31' or '2024-12-31T23:59:59') or natural language (e.g., 'tomorrow', 'next monday')."
                }

        task_data = TaskCreate(
            title=title,
            description=description,
            priority=priority_enum,
            due_date=due_date_obj,
            tags=tags
        )

        task = TaskService.create_task(session_obj, task_data, mock_user)

        return {
            "status": "created",
            "task_id": str(task.id),
            "title": task.title,
            "priority": task.priority.value,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "tags": task.tags
        }

    @function_tool(name_override="list_tasks")
    def list_tasks(
        ctx: RunContextWrapper[Any],
        status: Annotated[Optional[str], Field(default=None, description="Filter by status: 'pending', 'in_progress', 'completed', or omit for all tasks")] = None,
        limit: Annotated[int, Field(default=20, description="Maximum number of tasks to return (default: 20)")] = 20
    ) -> Dict[str, Any]:
        """List all tasks, optionally filtered by status (pending, in_progress, completed, or omit for all)"""
        session_obj, uid = _get_context(ctx)
        mock_user = User(id=uuid.UUID(uid))

        status_enum = None
        if status and status.lower() != "all":
            try:
                status_enum = TaskStatus(status.lower())
            except ValueError:
                pass

        tasks, count = TaskService.get_user_tasks(
            session=session_obj,
            current_user=mock_user,
            status=status_enum,
            limit=limit
        )

        return {
            "count": len(tasks),
            "total_count": count,
            "tasks": [
                {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "status": task.status.value,
                    "priority": task.priority.value,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "created_at": task.created_at.isoformat() if task.created_at else None
                }
                for task in tasks
            ]
        }

    @function_tool(name_override="complete_task")
    def complete_task(ctx: RunContextWrapper[Any], task_id: str) -> Dict[str, Any]:
        """Mark a task as completed using its ID or title"""
        session_obj, uid = _get_context(ctx)
        mock_user = User(id=uuid.UUID(uid))
        task, err = _resolve_and_validate_task(session_obj, task_id, mock_user)
        if err:
            return err
        task_update = TaskUpdate(status=TaskStatus.COMPLETED)
        updated_task = TaskService.update_task(session_obj, task.id, task_update, mock_user)
        return {"status": "completed", "task_id": str(updated_task.id), "title": updated_task.title}

    @function_tool(name_override="delete_task")
    def delete_task(ctx: RunContextWrapper[Any], task_id: str) -> Dict[str, Any]:
        """Delete a task using its ID or title"""
        session_obj, uid = _get_context(ctx)
        mock_user = User(id=uuid.UUID(uid))
        task, err = _resolve_and_validate_task(session_obj, task_id, mock_user)
        if err:
            return err
        task_id_val = task.id
        title = task.title
        TaskService.delete_task(session_obj, task_id_val, mock_user)
        return {"status": "deleted", "task_id": str(task_id_val), "title": title}

    @function_tool(name_override="update_task")
    def update_task(
        ctx: RunContextWrapper[Any],
        task_id: Annotated[str, Field(description="The task ID (UUID) or title to identify the task")],
        title: Annotated[Optional[str], Field(default=None, description="New title for the task (optional)")] = None,
        description: Annotated[Optional[str], Field(default=None, description="New description for the task (optional)")] = None,
        priority: Annotated[Optional[str], Field(default=None, description="New priority - 'low', 'medium', 'high', or 'urgent' (optional)")] = None,
        status: Annotated[Optional[str], Field(default=None, description="New status - 'pending', 'in_progress', or 'completed' (optional)")] = None,
        due_date: Annotated[Optional[str], Field(default=None, description="New due date. Accepts ISO format (e.g., '2024-12-31', '2024-12-31T23:59:59') or natural language (e.g., 'tomorrow', 'next monday', 'in 3 days') (optional)")] = None,
        tags: Annotated[Optional[List[str]], Field(default=None, description="New list of tags (replaces existing tags) (optional)")] = None
    ) -> Dict[str, Any]:
        """Update a task's title, description, priority, status, due date, or tags using its ID or title"""
        session_obj, uid = _get_context(ctx)
        mock_user = User(id=uuid.UUID(uid))
        task, err = _resolve_and_validate_task(session_obj, task_id, mock_user)
        if err:
            return err

        update_data = {}
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if priority is not None:
            try:
                update_data["priority"] = TaskPriority(priority.lower())
            except ValueError:
                pass
        if status is not None:
            try:
                update_data["status"] = TaskStatus(status.lower())
            except ValueError:
                pass
        if due_date:
            try:
                update_data["due_date"] = parser.parse(due_date)
            except (ValueError, TypeError) as e:
                return {"status": "error", "error": f"Invalid date format: {str(e)}. Please use ISO format or natural language."}
        if tags is not None:
            update_data["tags"] = tags

        if not update_data:
            return {"status": "no_change", "message": "No fields to update"}

        task_update = TaskUpdate(**update_data)
        updated_task = TaskService.update_task(session_obj, task.id, task_update, mock_user)
        return {
            "status": "updated",
            "task_id": str(updated_task.id),
            "title": updated_task.title,
            "priority": updated_task.priority.value,
            "task_status": updated_task.status.value,
            "due_date": updated_task.due_date.isoformat() if updated_task.due_date else None,
            "tags": updated_task.tags
        }

    @function_tool(name_override="bulk_complete")
    def bulk_complete(
        ctx: RunContextWrapper[Any],
        confirm: Annotated[bool, Field(default=True, description="Confirmation flag (always true)")] = True
    ) -> Dict[str, Any]:
        """Mark all your pending or in-progress tasks as completed"""
        session_obj, uid = _get_context(ctx)
        mock_user = User(id=uuid.UUID(uid))
        try:
            statement = select(Task).where(Task.user_id == mock_user.id, Task.status != TaskStatus.COMPLETED)
            tasks = session_obj.exec(statement).all()
            count = len(tasks)
            for task in tasks:
                TaskService.update_task(session_obj, task.id, TaskUpdate(status=TaskStatus.COMPLETED), mock_user)
            return {"status": "success", "message": f"Successfully completed {count} tasks.", "count": count}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @function_tool(name_override="bulk_delete")
    def bulk_delete(
        ctx: RunContextWrapper[Any],
        confirm: Annotated[bool, Field(default=True, description="Confirmation flag (always true)")] = True
    ) -> Dict[str, Any]:
        """Delete all your completed tasks"""
        session_obj, uid = _get_context(ctx)
        mock_user = User(id=uuid.UUID(uid))
        try:
            statement = select(Task).where(Task.user_id == mock_user.id, Task.status == TaskStatus.COMPLETED)
            tasks = session_obj.exec(statement).all()
            count = len(tasks)
            for task in tasks:
                TaskService.delete_task(session_obj, task.id, mock_user)
            return {"status": "success", "message": f"Successfully deleted {count} completed tasks.", "deleted_count": count}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @function_tool(name_override="clear_all")
    def clear_all(
        ctx: RunContextWrapper[Any],
        confirm: Annotated[bool, Field(default=True, description="Confirmation flag (always true)")] = True
    ) -> Dict[str, Any]:
        """Delete ALL your tasks (irreversible)"""
        session_obj, uid = _get_context(ctx)
        mock_user = User(id=uuid.UUID(uid))
        try:
            statement = select(Task).where(Task.user_id == mock_user.id)
            tasks = session_obj.exec(statement).all()
            count = len(tasks)
            for task in tasks:
                TaskService.delete_task(session_obj, task.id, mock_user)
            return {"status": "success", "message": f"Successfully deleted all {count} tasks.", "deleted_count": count}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    return [add_task, list_tasks, complete_task, delete_task, update_task, bulk_complete, bulk_delete, clear_all]


def create_task_tools(session: Session, user_id: str, thread_id: str = "") -> list[Any]:
    """Create MCP tools for task management"""
    return _build_task_tools(session, user_id, thread_id)
