"""Recurring pattern API router"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from src.auth.dependencies import get_current_user
from src.database import get_session
from src.models.user import User
from src.schemas.recurring_schemas import (
    RecurringPatternCreate,
    RecurringPatternUpdate,
    RecurringPatternRead
)
from src.services.recurring_service import RecurringPatternService

router = APIRouter(prefix="/recurring", tags=["recurring"])


@router.post("/", response_model=RecurringPatternRead, status_code=status.HTTP_201_CREATED)
async def create_recurring_pattern(
    pattern_data: RecurringPatternCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Create a new recurring pattern for a task

    Args:
        pattern_data: Recurring pattern creation data
        session: Database session
        current_user: Authenticated user

    Returns:
        Created recurring pattern

    Raises:
        HTTPException: If task doesn't exist or already has a pattern
    """
    return RecurringPatternService.create_pattern(session, pattern_data, current_user)


@router.get("/task/{task_id}", response_model=Optional[RecurringPatternRead])
async def get_task_recurring_pattern(
    task_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get recurring pattern for a specific task

    Args:
        task_id: Task UUID
        session: Database session
        current_user: Authenticated user

    Returns:
        Recurring pattern or None if not found
    """
    return RecurringPatternService.get_pattern_by_task(session, task_id, current_user)


@router.put("/{pattern_id}", response_model=RecurringPatternRead)
async def update_recurring_pattern(
    pattern_id: int,
    pattern_data: RecurringPatternUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Update a recurring pattern

    Args:
        pattern_id: Pattern ID
        pattern_data: Update data
        session: Database session
        current_user: Authenticated user

    Returns:
        Updated recurring pattern

    Raises:
        HTTPException: If pattern not found or doesn't belong to user
    """
    return RecurringPatternService.update_pattern(session, pattern_id, pattern_data, current_user)


@router.delete("/{pattern_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recurring_pattern(
    pattern_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Delete a recurring pattern

    Args:
        pattern_id: Pattern ID
        session: Database session
        current_user: Authenticated user

    Raises:
        HTTPException: If pattern not found or doesn't belong to user
    """
    RecurringPatternService.delete_pattern(session, pattern_id, current_user)
