"""MCP tools for task management operations

These tools are exposed to the AI agent via OpenAI Agents SDK,
allowing natural language task management.
"""
import uuid
from datetime import datetime
from typing import Any, Optional

from sqlmodel import Session, select
from agents import function_tool, RunContextWrapper

from src.models.task import Task, TaskStatus, TaskPriority


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


def create_task_tools(session: Session, user_id: str, thread_id: str = "") -> list[Any]:
    """Create MCP tools for task management

    Args:
        session: Database session
        user_id: User ID for data isolation
        thread_id: Current conversation/thread ID

    Returns:
        List of decorated function tools
    """
    context = TaskToolContext(session=session, user_id=user_id, thread_id=thread_id)

    @function_tool(name_override="add_task")
    def add_task(ctx: RunContextWrapper[TaskToolContext], title: str, description: str | None = None, priority: str = "medium") -> str:
        """Create a new task with a title and optional description and priority"""
        session = ctx.context.session
        user_id = ctx.context.user_id

        try:
            priority_enum = TaskPriority(priority.lower())
        except ValueError:
            priority_enum = TaskPriority.MEDIUM

        task = Task(
            title=title,
            description=description,
            priority=priority_enum,
            user_id=uuid.UUID(user_id),
            status=TaskStatus.PENDING
        )

        session.add(task)
        session.commit()
        session.refresh(task)

        return f"Task created successfully! ID: {task.id}, Title: {task.title}, Priority: {task.priority.value}"

    @function_tool(name_override="list_tasks")
    def list_tasks(ctx: RunContextWrapper[TaskToolContext], status: str | None = None, limit: int = 20) -> str:
        """List all tasks, optionally filtered by status (pending, in_progress, completed, or omit for all)"""
        session = ctx.context.session
        user_id = ctx.context.user_id

        statement = select(Task).where(Task.user_id == uuid.UUID(user_id))

        if status and status.lower() != "all":
            try:
                status_enum = TaskStatus(status.lower())
                statement = statement.where(Task.status == status_enum)
            except ValueError:
                pass

        statement = statement.order_by(Task.created_at.desc()).limit(limit)
        tasks = session.exec(statement).all()

        if not tasks:
            return "No tasks found."

        result = f"Found {len(tasks)} task(s):\n\n"
        for task in tasks:
            status_icon = "✓" if task.status == TaskStatus.COMPLETED else "○"
            result += f"{status_icon} [{task.status.value}] *{task.priority.value}* {task.title}"
            if task.description:
                result += f"\n   {task.description}"
            result += f"\n   ID: {task.id}\n\n"

        return result

    @function_tool(name_override="complete_task")
    def complete_task(ctx: RunContextWrapper[TaskToolContext], task_id: str) -> str:
        """Mark a task as completed using its ID"""
        session = ctx.context.session
        user_id = ctx.context.user_id

        try:
            task_uuid = uuid.UUID(task_id)
        except ValueError:
            return f"Error: Invalid task ID format: {task_id}"

        statement = select(Task).where(
            Task.id == task_uuid,
            Task.user_id == uuid.UUID(user_id)
        )
        task = session.exec(statement).first()

        if not task:
            return f"Error: Task not found with ID: {task_id}"

        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()

        session.add(task)
        session.commit()

        return f"Task completed! Title: {task.title}"

    @function_tool(name_override="delete_task")
    def delete_task(ctx: RunContextWrapper[TaskToolContext], task_id: str) -> str:
        """Delete a task using its ID"""
        session = ctx.context.session
        user_id = ctx.context.user_id

        try:
            task_uuid = uuid.UUID(task_id)
        except ValueError:
            return f"Error: Invalid task ID format: {task_id}"

        statement = select(Task).where(
            Task.id == task_uuid,
            Task.user_id == uuid.UUID(user_id)
        )
        task = session.exec(statement).first()

        if not task:
            return f"Error: Task not found with ID: {task_id}"

        title = task.title
        session.delete(task)
        session.commit()

        return f"Task deleted! Title: {title}"

    @function_tool(name_override="update_task")
    def update_task(ctx: RunContextWrapper[TaskToolContext], task_id: str, title: str | None = None, description: str | None = None, priority: str | None = None, status: str | None = None) -> str:
        """Update a task's title, description, priority, or status"""
        session = ctx.context.session
        user_id = ctx.context.user_id

        try:
            task_uuid = uuid.UUID(task_id)
        except ValueError:
            return f"Error: Invalid task ID format: {task_id}"

        statement = select(Task).where(
            Task.id == task_uuid,
            Task.user_id == uuid.UUID(user_id)
        )
        task = session.exec(statement).first()

        if not task:
            return f"Error: Task not found with ID: {task_id}"

        updated = []
        if title is not None:
            task.title = title
            updated.append("title")
        if description is not None:
            task.description = description
            updated.append("description")
        if priority is not None:
            try:
                task.priority = TaskPriority(priority.lower())
                updated.append("priority")
            except ValueError:
                pass
        if status is not None:
            try:
                new_status = TaskStatus(status.lower())
                task.status = new_status
                updated.append("status")
                if new_status == TaskStatus.COMPLETED:
                    task.completed_at = datetime.utcnow()
                else:
                    task.completed_at = None
            except ValueError:
                pass

        if not updated:
            return "No fields to update"

        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()

        return f"Task updated! Changed fields: {', '.join(updated)}. Title: {task.title}"

    return [add_task, list_tasks, complete_task, delete_task, update_task]
