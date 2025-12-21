"""TodoApp service class with CRUD operations for task management."""

import logging
import os
from typing import List, Optional

from sqlmodel import Session, select

from src.models import Task, PriorityEnum, StatusEnum, get_engine, create_db_and_tables

logger = logging.getLogger(__name__)


class TodoApp:
    """
    Service class for managing todo tasks with SQLite persistence.

    Provides methods for creating, reading, updating, and deleting tasks.
    """

    def __init__(self):
        """Initialize TodoApp and create database tables."""
        logger.info("Initializing TodoApp...")
        create_db_and_tables()
        self._initialize_default_task()
        logger.info("TodoApp initialized successfully")

    def _initialize_default_task(self) -> None:
        """Create default task on first run if no tasks exist."""
        with Session(get_engine()) as session:
            # Check if any tasks exist
            statement = select(Task)
            tasks = session.exec(statement).all()

            if not tasks:
                # Get user's name from environment or use default
                user_name = os.getenv("USER", os.getenv("USERNAME", "User"))
                default_task = Task(
                    title=f"{user_name}'s first todo",
                    description="Welcome to your todo app! Edit or delete this task to get started.",
                    priority=PriorityEnum.MEDIUM,
                    status=StatusEnum.PENDING,
                )
                session.add(default_task)
                session.commit()

    def add_task(
        self,
        title: str,
        description: str = "",
        priority: str = "Medium",
    ) -> Task:
        """
        Create a new task.

        Args:
            title: Task title (1-200 characters)
            description: Optional task description (max 500 characters)
            priority: Priority level (Low, Medium, High)

        Returns:
            Task: Created task with assigned ID

        Raises:
            ValueError: If validation fails
        """
        # Normalize priority
        priority_map = {
            "LOW": PriorityEnum.LOW,
            "MEDIUM": PriorityEnum.MEDIUM,
            "HIGH": PriorityEnum.HIGH,
        }
        priority_enum = priority_map.get(priority.upper(), PriorityEnum.MEDIUM)

        task = Task(
            title=title,
            description=description,
            priority=priority_enum,
            status=StatusEnum.PENDING,
        )

        with Session(get_engine()) as session:
            session.add(task)
            session.commit()
            session.refresh(task)
            logger.info(f"Task created: ID={task.id}, title='{task.title}'")
            return task

    def view_tasks(self) -> List[Task]:
        """
        Retrieve all tasks.

        Returns:
            List[Task]: List of all tasks, ordered by ID
        """
        with Session(get_engine()) as session:
            statement = select(Task).order_by(Task.id)
            tasks = session.exec(statement).all()
            return list(tasks)

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """
        Retrieve a single task by ID.

        Args:
            task_id: Task ID to retrieve

        Returns:
            Optional[Task]: Task if found, None otherwise
        """
        with Session(get_engine()) as session:
            return session.get(Task, task_id)

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[Task]:
        """
        Update an existing task.

        Args:
            task_id: ID of task to update
            title: New title (if provided)
            description: New description (if provided)

        Returns:
            Optional[Task]: Updated task if found, None otherwise

        Raises:
            ValueError: If task not found or validation fails
        """
        with Session(get_engine()) as session:
            task = session.get(Task, task_id)
            if not task:
                return None

            if title is not None:
                task.title = title
            if description is not None:
                task.description = description

            session.add(task)
            session.commit()
            session.refresh(task)
            return task

    def mark_task(self, task_id: int, status: str) -> Optional[Task]:
        """
        Update task status.

        Args:
            task_id: ID of task to update
            status: New status (Pending, In-Progress, Completed)

        Returns:
            Optional[Task]: Updated task if found, None otherwise

        Raises:
            ValueError: If task not found or status invalid
        """
        # Normalize status
        status_normalized = status.replace(" ", "-").replace("_", "-").upper()
        status_map = {
            "PENDING": StatusEnum.PENDING,
            "IN-PROGRESS": StatusEnum.IN_PROGRESS,
            "COMPLETED": StatusEnum.COMPLETED,
        }
        status_enum = status_map.get(status_normalized)

        if not status_enum:
            raise ValueError(f"Invalid status: {status}")

        with Session(get_engine()) as session:
            task = session.get(Task, task_id)
            if not task:
                return None

            task.status = status_enum
            session.add(task)
            session.commit()
            session.refresh(task)
            return task

    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task by ID.

        Args:
            task_id: ID of task to delete

        Returns:
            bool: True if task was deleted, False if not found
        """
        with Session(get_engine()) as session:
            task = session.get(Task, task_id)
            if not task:
                logger.warning(f"Attempted to delete non-existent task: ID={task_id}")
                return False

            session.delete(task)
            session.commit()
            logger.info(f"Task deleted: ID={task_id}")
            return True
