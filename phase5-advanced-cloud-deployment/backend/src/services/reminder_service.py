"""Reminder service for managing task reminders"""
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlmodel import Session, select
from src.models.reminder import Reminder
from src.models.user import User
from src.schemas.reminder_schemas import ReminderCreate, ReminderUpdate

REMINDER_NOT_FOUND = "Reminder not found"


class ReminderService:
    """Service for reminder operations with user isolation"""

    @staticmethod
    def create_reminder(
        session: Session,
        reminder_data: ReminderCreate,
        current_user: User
    ) -> Reminder:
        """Create a new reminder for a task

        Args:
            session: Database session
            reminder_data: Reminder creation data
            current_user: Authenticated user

        Returns:
            Created reminder

        Raises:
            HTTPException: If task doesn't exist or doesn't belong to user
        """
        # Verify task exists and belongs to user
        from src.models.task import Task
        task = session.get(Task, reminder_data.task_id)
        if not task or task.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Validate remind_at is before task due_date if due_date exists
        if task.due_date and reminder_data.remind_at >= task.due_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reminder time must be before task due date"
            )

        reminder = Reminder(
            **reminder_data.model_dump(),
            user_id=current_user.id
        )
        session.add(reminder)
        session.commit()
        session.refresh(reminder)
        return reminder

    @staticmethod
    def get_task_reminders(
        session: Session,
        task_id: UUID,
        current_user: User
    ) -> List[Reminder]:
        """Get all reminders for a task

        Args:
            session: Database session
            task_id: Task UUID
            current_user: Authenticated user

        Returns:
            List of reminders
        """
        reminders = session.exec(
            select(Reminder).where(
                Reminder.task_id == task_id,
                Reminder.user_id == current_user.id
            ).order_by(Reminder.remind_at)
        ).all()
        return list(reminders)

    @staticmethod
    def get_pending_reminders(
        session: Session,
        current_user: User,
        before: Optional[datetime] = None
    ) -> List[Reminder]:
        """Get pending reminders for a user

        Args:
            session: Database session
            current_user: Authenticated user
            before: Optional cutoff time (default: now)

        Returns:
            List of pending reminders
        """
        if before is None:
            before = datetime.now(timezone.utc)

        reminders = session.exec(
            select(Reminder).where(
                Reminder.user_id == current_user.id,
                Reminder.sent == False,
                Reminder.remind_at <= before
            ).order_by(Reminder.remind_at)
        ).all()
        return list(reminders)

    @staticmethod
    def update_reminder(
        session: Session,
        reminder_id: int,
        reminder_data: ReminderUpdate,
        current_user: User
    ) -> Reminder:
        """Update a reminder

        Args:
            session: Database session
            reminder_id: Reminder ID
            reminder_data: Update data
            current_user: Authenticated user

        Returns:
            Updated reminder

        Raises:
            HTTPException: If reminder not found or doesn't belong to user
        """
        reminder = session.get(Reminder, reminder_id)
        if not reminder or reminder.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=REMINDER_NOT_FOUND
            )

        # Update fields
        update_data = reminder_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(reminder, key, value)

        session.add(reminder)
        session.commit()
        session.refresh(reminder)
        return reminder

    @staticmethod
    def mark_reminder_sent(
        session: Session,
        reminder_id: int,
        current_user: User
    ) -> Reminder:
        """Mark a reminder as sent

        Args:
            session: Database session
            reminder_id: Reminder ID
            current_user: Authenticated user

        Returns:
            Updated reminder

        Raises:
            HTTPException: If reminder not found or doesn't belong to user
        """
        reminder = session.get(Reminder, reminder_id)
        if not reminder or reminder.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=REMINDER_NOT_FOUND
            )

        reminder.sent = True
        reminder.sent_at = datetime.now(timezone.utc)
        session.add(reminder)
        session.commit()
        session.refresh(reminder)
        return reminder

    @staticmethod
    def delete_reminder(
        session: Session,
        reminder_id: int,
        current_user: User
    ) -> None:
        """Delete a reminder

        Args:
            session: Database session
            reminder_id: Reminder ID
            current_user: Authenticated user

        Raises:
            HTTPException: If reminder not found or doesn't belong to user
        """
        reminder = session.get(Reminder, reminder_id)
        if not reminder or reminder.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=REMINDER_NOT_FOUND
            )

        session.delete(reminder)
        session.commit()

    @staticmethod
    def create_reminder_from_task(
        session: Session,
        task_id: UUID,
        current_user: User
    ) -> Optional[Reminder]:
        """Create a reminder based on task's due_date and reminder_offset

        Args:
            session: Database session
            task_id: Task UUID
            current_user: Authenticated user

        Returns:
            Created reminder or None if task has no due_date

        Raises:
            HTTPException: If task doesn't exist or doesn't belong to user
        """
        from src.models.task import Task
        task = session.get(Task, task_id)
        if not task or task.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Only create reminder if task has a due_date
        if not task.due_date:
            return None

        # Calculate remind_at based on due_date and reminder_offset
        remind_at = task.due_date - timedelta(minutes=task.reminder_offset)

        # Don't create reminder if remind_at is in the past
        if remind_at < datetime.now(timezone.utc):
            return None

        reminder = Reminder(
            task_id=task_id,
            user_id=current_user.id,
            remind_at=remind_at
        )
        session.add(reminder)
        session.commit()
        session.refresh(reminder)
        return reminder
