"""Task service with user isolation enforcement"""
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlmodel import Session, select, func, col, case
from sqlalchemy import literal_column
from src.models.task import Task, TaskStatus, TaskPriority
from src.models.user import User
from src.schemas.task_schemas import TaskCreate, TaskUpdate, SortField, SortOrder


class TaskService:
    """Service for task operations with user isolation

    All methods enforce user_id filtering to ensure data isolation
    """

    @staticmethod
    def create_task(
        session: Session,
        task_data: TaskCreate,
        current_user: User
    ) -> Task:
        """Create a new task for the current user

        Args:
            session: Database session
            task_data: Task creation data
            current_user: Authenticated user

        Returns:
            Created task
        """
        task = Task(
            **task_data.model_dump(),
            user_id=current_user.id
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    @staticmethod
    def get_user_tasks(
        session: Session,
        current_user: User,
        status: Optional[TaskStatus] = None,
        priority: Optional[str] = None,
        sort_by: Optional[SortField] = SortField.CREATED_AT,
        sort_order: Optional[SortOrder] = SortOrder.DESC,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[List[Task], int]:
        """Get tasks for the current user with optional filtering and sorting

        Args:
            session: Database session
            current_user: Authenticated user
            status: Optional status filter
            priority: Optional priority filter
            sort_by: Field to sort by (default: created_at)
            sort_order: Sort direction (default: desc)
            limit: Maximum number of tasks to return
            offset: Number of tasks to skip

        Returns:
            Tuple of (list of tasks, total count)
        """
        # Build query with user_id filter (CRITICAL for data isolation)
        statement = select(Task).where(Task.user_id == current_user.id)

        # Apply filters
        if status:
            statement = statement.where(Task.status == status)
        if priority:
            statement = statement.where(Task.priority == priority)

        # Get total count
        count_statement = select(func.count()).select_from(statement.subquery())
        total = session.exec(count_statement).one()

        # Apply sorting based on parameters
        # NULL values handling: tasks without due dates appear last when sorting by due_date
        if sort_by == SortField.DUE_DATE:
            # For ascending: NULL values come last (PostgreSQL default)
            # For descending: NULL values come last (we want tasks with due dates first)
            if sort_order == SortOrder.ASC:
                statement = statement.order_by(col(Task.due_date).asc().nulls_last())
            else:
                statement = statement.order_by(col(Task.due_date).desc().nulls_last())
        elif sort_by == SortField.PRIORITY:
            # Sort by TaskPriority enum order using CASE expression
            # Priority order: LOW(1) < MEDIUM(2) < HIGH(3) < URGENT(4)
            priority_case = case(
                (Task.priority == TaskPriority.LOW, 1),
                (Task.priority == TaskPriority.MEDIUM, 2),
                (Task.priority == TaskPriority.HIGH, 3),
                (Task.priority == TaskPriority.URGENT, 4),
                else_=0  # Fallback
            )
            if sort_order == SortOrder.ASC:
                statement = statement.order_by(priority_case.asc())
            else:
                statement = statement.order_by(priority_case.desc())
        elif sort_by == SortField.TITLE:
            # Case-insensitive alphabetical sort
            if sort_order == SortOrder.ASC:
                statement = statement.order_by(col(Task.title).asc())
            else:
                statement = statement.order_by(col(Task.title).desc())
        else:
            # Default: sort by created_at
            if sort_order == SortOrder.ASC:
                statement = statement.order_by(Task.created_at.asc())
            else:
                statement = statement.order_by(Task.created_at.desc())

        # Apply pagination
        statement = statement.offset(offset).limit(limit)

        tasks = session.exec(statement).all()
        return list(tasks), total

    @staticmethod
    def get_task_by_id(
        session: Session,
        task_id: UUID,
        current_user: User
    ) -> Task:
        """Get a specific task by ID for the current user

        Args:
            session: Database session
            task_id: Task ID
            current_user: Authenticated user

        Returns:
            Task if found and owned by user

        Raises:
            HTTPException: If task not found or not owned by user
        """
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == current_user.id  # CRITICAL: User isolation
        )
        task = session.exec(statement).first()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        return task

    @staticmethod
    def update_task(
        session: Session,
        task_id: UUID,
        task_data: TaskUpdate,
        current_user: User
    ) -> Task:
        """Update a task for the current user

        Args:
            session: Database session
            task_id: Task ID
            task_data: Task update data
            current_user: Authenticated user

        Returns:
            Updated task

        Raises:
            HTTPException: If task not found or not owned by user
        """
        task = TaskService.get_task_by_id(session, task_id, current_user)

        # Update fields
        update_data = task_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(task, key, value)

        # Handle status transitions and completed_at
        if 'status' in update_data:
            if task.status == TaskStatus.COMPLETED and task.completed_at is None:
                task.completed_at = datetime.now(timezone.utc)
            elif task.status != TaskStatus.COMPLETED:
                task.completed_at = None

        task.updated_at = datetime.now(timezone.utc)

        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    @staticmethod
    def delete_task(
        session: Session,
        task_id: UUID,
        current_user: User
    ) -> None:
        """Delete a task for the current user

        Args:
            session: Database session
            task_id: Task ID
            current_user: Authenticated user

        Raises:
            HTTPException: If task not found or not owned by user
        """
        task = TaskService.get_task_by_id(session, task_id, current_user)
        session.delete(task)
        session.commit()
