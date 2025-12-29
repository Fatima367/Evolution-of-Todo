"""MCP tools for task management operations

These tools are exposed to the AI agent via OpenAI Agents SDK,
allowing natural language task management.
"""
import uuid
from typing import Optional, Literal
from datetime import datetime

from sqlmodel import Session, select
from agents import Tool

from src.models.task import Task, TaskStatus, TaskPriority
from src.models.user import User


def create_task_tools(session: Session, user_id: str) -> list[Tool]:
    """Create MCP tools for task management

    Args:
        session: Database session
        user_id: User ID for data isolation

    Returns:
        List of Tool objects for the AI agent
    """

    def add_task(title: str, description: Optional[str] = None, priority: str = "medium") -> dict:
        """Create a new task

        Args:
            title: Task title (required)
            description: Task description (optional)
            priority: Task priority (low, medium, high, urgent)

        Returns:
            Dictionary with task_id, status, and title
        """
        try:
            # Validate priority
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

        return {
            "task_id": str(task.id),
            "status": "created",
            "title": task.title,
            "priority": task.priority.value
        }

    def list_tasks(status: Optional[str] = None, limit: int = 20) -> dict:
        """List user's tasks with optional filtering

        Args:
            status: Filter by status (pending, in_progress, completed, or omit for all)
            limit: Maximum number of tasks to return (default 20)

        Returns:
            Dictionary with tasks array
        """
        statement = select(Task).where(Task.user_id == uuid.UUID(user_id))

        # Apply status filter
        if status and status.lower() != "all":
            try:
                status_enum = TaskStatus(status.lower())
                statement = statement.where(Task.status == status_enum)
            except ValueError:
                pass

        # Order by creation date (newest first)
        statement = statement.order_by(Task.created_at.desc()).limit(limit)

        tasks = session.exec(statement).all()

        return {
            "tasks": [
                {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "status": task.status.value,
                    "priority": task.priority.value,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "created_at": task.created_at.isoformat()
                }
                for task in tasks
            ],
            "count": len(tasks)
        }

    def complete_task(task_id: str) -> dict:
        """Mark a task as completed

        Args:
            task_id: Task ID to complete

        Returns:
            Dictionary with task_id, status, and title
        """
        try:
            task_uuid = uuid.UUID(task_id)
        except ValueError:
            return {"error": "Invalid task ID format", "status": "error"}

        statement = select(Task).where(
            Task.id == task_uuid,
            Task.user_id == uuid.UUID(user_id)
        )
        task = session.exec(statement).first()

        if not task:
            return {"error": "Task not found", "status": "error"}

        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()

        session.add(task)
        session.commit()

        return {
            "task_id": str(task.id),
            "status": "completed",
            "title": task.title
        }

    def delete_task(task_id: str) -> dict:
        """Delete a task

        Args:
            task_id: Task ID to delete

        Returns:
            Dictionary with task_id, status, and title
        """
        try:
            task_uuid = uuid.UUID(task_id)
        except ValueError:
            return {"error": "Invalid task ID format", "status": "error"}

        statement = select(Task).where(
            Task.id == task_uuid,
            Task.user_id == uuid.UUID(user_id)
        )
        task = session.exec(statement).first()

        if not task:
            return {"error": "Task not found", "status": "error"}

        title = task.title
        session.delete(task)
        session.commit()

        return {
            "task_id": task_id,
            "status": "deleted",
            "title": title
        }

    def update_task(
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None
    ) -> dict:
        """Update a task's details

        Args:
            task_id: Task ID to update
            title: New title (optional)
            description: New description (optional)
            priority: New priority (optional: low, medium, high, urgent)
            status: New status (optional: pending, in_progress, completed)

        Returns:
            Dictionary with task_id, status, and title
        """
        try:
            task_uuid = uuid.UUID(task_id)
        except ValueError:
            return {"error": "Invalid task ID format", "status": "error"}

        statement = select(Task).where(
            Task.id == task_uuid,
            Task.user_id == uuid.UUID(user_id)
        )
        task = session.exec(statement).first()

        if not task:
            return {"error": "Task not found", "status": "error"}

        # Update fields
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if priority is not None:
            try:
                task.priority = TaskPriority(priority.lower())
            except ValueError:
                pass
        if status is not None:
            try:
                new_status = TaskStatus(status.lower())
                task.status = new_status
                if new_status == TaskStatus.COMPLETED:
                    task.completed_at = datetime.utcnow()
                else:
                    task.completed_at = None
            except ValueError:
                pass

        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()

        return {
            "task_id": str(task.id),
            "status": "updated",
            "title": task.title,
            "priority": task.priority.value,
            "task_status": task.status.value
        }

    # Create Tool objects with proper schemas
    tools = [
        Tool(
            name="add_task",
            description="Create a new task with a title and optional description and priority",
            func=add_task
        ),
        Tool(
            name="list_tasks",
            description="List all tasks, optionally filtered by status (pending/in_progress/completed/all)",
            func=list_tasks
        ),
        Tool(
            name="complete_task",
            description="Mark a task as completed using its ID",
            func=complete_task
        ),
        Tool(
            name="delete_task",
            description="Delete a task using its ID",
            func=delete_task
        ),
        Tool(
            name="update_task",
            description="Update a task's title, description, priority, or status",
            func=update_task
        ),
    ]

    return tools
