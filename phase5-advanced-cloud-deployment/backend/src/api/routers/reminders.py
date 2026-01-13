"""Reminder API router"""
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from src.auth.dependencies import get_current_user
from src.database import get_session
from src.models.user import User
from src.schemas.reminder_schemas import (
    ReminderCreate,
    ReminderUpdate,
    ReminderRead
)
from src.services.reminder_service import ReminderService

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.post("/", response_model=ReminderRead, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    reminder_data: ReminderCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Create a new reminder for a task

    Args:
        reminder_data: Reminder creation data
        session: Database session
        current_user: Authenticated user

    Returns:
        Created reminder

    Raises:
        HTTPException: If task doesn't exist or doesn't belong to user
    """
    return ReminderService.create_reminder(session, reminder_data, current_user)


@router.get("/task/{task_id}", response_model=List[ReminderRead])
async def get_task_reminders(
    task_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get all reminders for a specific task

    Args:
        task_id: Task UUID
        session: Database session
        current_user: Authenticated user

    Returns:
        List of reminders for the task
    """
    return ReminderService.get_task_reminders(session, task_id, current_user)


@router.get("/pending", response_model=List[ReminderRead])
async def get_pending_reminders(
    before: Optional[datetime] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get pending reminders for the current user

    Args:
        before: Optional cutoff time (default: now)
        session: Database session
        current_user: Authenticated user

    Returns:
        List of pending reminders
    """
    return ReminderService.get_pending_reminders(session, current_user, before)


@router.put("/{reminder_id}", response_model=ReminderRead)
async def update_reminder(
    reminder_id: int,
    reminder_data: ReminderUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Update a reminder

    Args:
        reminder_id: Reminder ID
        reminder_data: Update data
        session: Database session
        current_user: Authenticated user

    Returns:
        Updated reminder

    Raises:
        HTTPException: If reminder not found or doesn't belong to user
    """
    return ReminderService.update_reminder(session, reminder_id, reminder_data, current_user)


@router.post("/{reminder_id}/mark-sent", response_model=ReminderRead)
async def mark_reminder_sent(
    reminder_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Mark a reminder as sent

    Args:
        reminder_id: Reminder ID
        session: Database session
        current_user: Authenticated user

    Returns:
        Updated reminder

    Raises:
        HTTPException: If reminder not found or doesn't belong to user
    """
    return ReminderService.mark_reminder_sent(session, reminder_id, current_user)


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder(
    reminder_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Delete a reminder

    Args:
        reminder_id: Reminder ID
        session: Database session
        current_user: Authenticated user

    Raises:
        HTTPException: If reminder not found or doesn't belong to user
    """
    ReminderService.delete_reminder(session, reminder_id, current_user)


@router.post("/task/{task_id}/auto-create", response_model=Optional[ReminderRead])
async def auto_create_reminder(
    task_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Automatically create a reminder based on task's due_date and reminder_offset

    Args:
        task_id: Task UUID
        session: Database session
        current_user: Authenticated user

    Returns:
        Created reminder or None if task has no due_date

    Raises:
        HTTPException: If task doesn't exist or doesn't belong to user
    """
    return ReminderService.create_reminder_from_task(session, task_id, current_user)
