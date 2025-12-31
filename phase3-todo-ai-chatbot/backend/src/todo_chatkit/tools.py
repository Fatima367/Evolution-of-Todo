"""MCP tools for task management operations

These tools are exposed to the AI agent via OpenAI Agents SDK,
allowing natural language task management.
"""
import uuid
from datetime import datetime
from typing import Any, Optional, Dict

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


def create_task_tools(session: Session, user_id: str, thread_id: str = "") -> list[Any]:
    """Create MCP tools for task management

    Args:
        session: Database session
        user_id: User ID for data isolation
        thread_id: Current conversation/thread ID

    Returns:
        List of decorated function tools
    """

    @function_tool(name_override="add_task")
    def add_task(ctx: RunContextWrapper[Any], title: str, description: str | None = None, priority: str = "medium") -> Dict[str, Any]:
        """Create a new task with a title and optional description and priority"""
        session_obj, uid = get_tool_context(ctx)
        if not session_obj or not uid:
            # Fallback to closure-captured values if context is missing
            session_obj, uid = session, user_id

        mock_user = User(id=uuid.UUID(uid))

        try:
            priority_enum = TaskPriority(priority.lower())
        except ValueError:
            priority_enum = TaskPriority.MEDIUM

        task_data = TaskCreate(
            title=title,
            description=description,
            priority=priority_enum
        )

        task = TaskService.create_task(session_obj, task_data, mock_user)

        return {
            "status": "created",
            "task_id": str(task.id),
            "title": task.title,
            "priority": task.priority.value
        }

    @function_tool(name_override="list_tasks")
    def list_tasks(ctx: RunContextWrapper[Any], status: str | None = None, limit: int = 20) -> Dict[str, Any]:
        """List all tasks, optionally filtered by status (pending, in_progress, completed, or omit for all)"""
        session_obj, uid = get_tool_context(ctx)
        if not session_obj or not uid:
            session_obj, uid = session, user_id

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
        """Mark a task as completed using its ID"""
        session_obj, uid = get_tool_context(ctx)
        if not session_obj or not uid:
            session_obj, uid = session, user_id

        mock_user = User(id=uuid.UUID(uid))

        try:
            task_uuid = uuid.UUID(task_id)
        except ValueError:
            return {"status": "error", "error": f"Invalid task ID format: {task_id}"}

        try:
            task_update = TaskUpdate(status=TaskStatus.COMPLETED)
            task = TaskService.update_task(session_obj, task_uuid, task_update, mock_user)
            return {
                "status": "completed",
                "task_id": str(task.id),
                "title": task.title
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @function_tool(name_override="delete_task")
    def delete_task(ctx: RunContextWrapper[Any], task_id: str) -> Dict[str, Any]:
        """Delete a task using its ID"""
        session_obj, uid = get_tool_context(ctx)
        if not session_obj or not uid:
            session_obj, uid = session, user_id

        mock_user = User(id=uuid.UUID(uid))

        try:
            task_uuid = uuid.UUID(task_id)
        except ValueError:
            return {"status": "error", "error": f"Invalid task ID format: {task_id}"}

        try:
            # Get task first to have its title for the response
            statement = select(Task).where(Task.id == task_uuid, Task.user_id == mock_user.id)
            task = session_obj.exec(statement).first()
            if not task:
                return {"status": "error", "error": "Task not found"}
            title = task.title

            TaskService.delete_task(session_obj, task_uuid, mock_user)
            return {
                "status": "deleted",
                "task_id": task_id,
                "title": title
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @function_tool(name_override="update_task")
    def update_task(ctx: RunContextWrapper[Any], task_id: str, title: str | None = None, description: str | None = None, priority: str | None = None, status: str | None = None) -> Dict[str, Any]:
        """Update a task's title, description, priority, or status"""
        session_obj, uid = get_tool_context(ctx)
        if not session_obj or not uid:
            session_obj, uid = session, user_id

        mock_user = User(id=uuid.UUID(uid))

        try:
            task_uuid = uuid.UUID(task_id)
        except ValueError:
            return {"status": "error", "error": f"Invalid task ID format: {task_id}"}

        update_data = {}
        if title is not None: update_data["title"] = title
        if description is not None: update_data["description"] = description
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

        if not update_data:
            return {"status": "no_change", "message": "No fields to update"}

        try:
            task_update = TaskUpdate(**update_data)
            task = TaskService.update_task(session_obj, task_uuid, task_update, mock_user)
            return {
                "status": "updated",
                "task_id": str(task.id),
                "title": task.title,
                "priority": task.priority.value,
                "task_status": task.status.value
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    return [add_task, list_tasks, complete_task, delete_task, update_task]
