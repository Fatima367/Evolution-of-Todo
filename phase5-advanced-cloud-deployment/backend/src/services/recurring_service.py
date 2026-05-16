"""Recurring pattern service for managing recurring tasks"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlmodel import Session, select
from src.models.recurring_pattern import RecurringPattern
from src.models.user import User
from src.schemas.recurring_schemas import RecurringPatternCreate, RecurringPatternUpdate


class RecurringPatternService:
    """Service for recurring pattern operations with user isolation"""

    @staticmethod
    def create_pattern(
        session: Session,
        pattern_data: RecurringPatternCreate,
        current_user: User
    ) -> RecurringPattern:
        """Create a new recurring pattern for a task

        Args:
            session: Database session
            pattern_data: Recurring pattern creation data
            current_user: Authenticated user

        Returns:
            Created recurring pattern

        Raises:
            HTTPException: If task doesn't exist or already has a pattern
        """
        # Verify task exists and belongs to user
        from src.models.task import Task
        task = session.get(Task, pattern_data.task_id)
        if not task or task.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Check if pattern already exists for this task
        existing = session.exec(
            select(RecurringPattern).where(RecurringPattern.task_id == pattern_data.task_id)
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task already has a recurring pattern"
            )

        pattern = RecurringPattern(
            **pattern_data.model_dump(),
            user_id=current_user.id
        )
        session.add(pattern)
        session.commit()
        session.refresh(pattern)
        return pattern

    @staticmethod
    def get_pattern_by_task(
        session: Session,
        task_id: UUID,
        current_user: User
    ) -> Optional[RecurringPattern]:
        """Get recurring pattern for a task

        Args:
            session: Database session
            task_id: Task UUID
            current_user: Authenticated user

        Returns:
            Recurring pattern or None if not found
        """
        pattern = session.exec(
            select(RecurringPattern).where(
                RecurringPattern.task_id == task_id,
                RecurringPattern.user_id == current_user.id
            )
        ).first()
        return pattern

    @staticmethod
    def update_pattern(
        session: Session,
        pattern_id: int,
        pattern_data: RecurringPatternUpdate,
        current_user: User
    ) -> RecurringPattern:
        """Update a recurring pattern

        Args:
            session: Database session
            pattern_id: Pattern ID
            pattern_data: Update data
            current_user: Authenticated user

        Returns:
            Updated recurring pattern

        Raises:
            HTTPException: If pattern not found or doesn't belong to user
        """
        pattern = session.get(RecurringPattern, pattern_id)
        if not pattern or pattern.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recurring pattern not found"
            )

        # Update fields
        update_data = pattern_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(pattern, key, value)

        pattern.updated_at = datetime.now(timezone.utc)
        session.add(pattern)
        session.commit()
        session.refresh(pattern)
        return pattern

    @staticmethod
    def delete_pattern(
        session: Session,
        pattern_id: int,
        current_user: User
    ) -> None:
        """Delete a recurring pattern

        Args:
            session: Database session
            pattern_id: Pattern ID
            current_user: Authenticated user

        Raises:
            HTTPException: If pattern not found or doesn't belong to user
        """
        pattern = session.get(RecurringPattern, pattern_id)
        if not pattern or pattern.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recurring pattern not found"
            )

        session.delete(pattern)
        session.commit()

    @staticmethod
    def calculate_next_occurrence(pattern: RecurringPattern, current_date: datetime) -> Optional[datetime]:
        """Calculate the next occurrence date for a recurring pattern

        Args:
            pattern: Recurring pattern
            current_date: Current date/time

        Returns:
            Next occurrence date or None if pattern has ended
        """
        # Check if pattern has ended
        if pattern.end_date and current_date >= pattern.end_date:
            return None

        next_date = current_date

        if pattern.frequency == 'daily':
            next_date = current_date + timedelta(days=pattern.interval)

        elif pattern.frequency == 'weekly':
            # Calculate next occurrence on the specified day of week
            days_ahead = pattern.day_of_week - current_date.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7 * pattern.interval
            next_date = current_date + timedelta(days=days_ahead)

        elif pattern.frequency == 'monthly':
            # Calculate next occurrence on the specified day of month
            month = current_date.month
            year = current_date.year

            # Add interval months
            month += pattern.interval
            while month > 12:
                month -= 12
                year += 1

            # Handle day overflow (e.g., Feb 31 -> Feb 28/29)
            try:
                next_date = current_date.replace(year=year, month=month, day=pattern.day_of_month)
            except ValueError:
                # Day doesn't exist in target month, use last day of month
                import calendar
                last_day = calendar.monthrange(year, month)[1]
                next_date = current_date.replace(year=year, month=month, day=last_day)

        elif pattern.frequency == 'yearly':
            # Calculate next occurrence on the specified month and day
            year = current_date.year + pattern.interval
            try:
                next_date = current_date.replace(
                    year=year,
                    month=pattern.month_of_year,
                    day=pattern.day_of_month
                )
            except ValueError:
                # Handle Feb 29 on non-leap years
                import calendar
                last_day = calendar.monthrange(year, pattern.month_of_year)[1]
                next_date = current_date.replace(
                    year=year,
                    month=pattern.month_of_year,
                    day=min(pattern.day_of_month, last_day)
                )

        # Check if next occurrence is beyond end_date
        if pattern.end_date and next_date >= pattern.end_date:
            return None

        return next_date
