"""Task management API endpoints"""
from typing import Annotated, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session
from src.database import get_session
from src.auth.dependencies import get_current_user
from src.models.user import User
from src.models.task import TaskStatus, TaskPriority
from src.schemas.task_schemas import TaskCreate, TaskRead, TaskUpdate, TaskListResponse, SortField, SortOrder
from src.services.task_service import TaskService


router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/", response_model=TaskListResponse)
async def get_tasks(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    status_filter: Optional[TaskStatus] = Query(None, alias="status", description="Filter by status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by priority"),
    is_favorite: Optional[bool] = Query(None, description="Filter by favorite status"),
    sort_by: Optional[SortField] = Query(SortField.CREATED_AT, description="Field to sort by"),
    sort_order: Optional[SortOrder] = Query(SortOrder.DESC, description="Sort direction"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of tasks"),
    offset: int = Query(0, ge=0, description="Number of tasks to skip")
):
    """Get all tasks for the authenticated user with optional filtering and sorting

    Enforces user isolation by filtering tasks by current_user.id
    """
    tasks, total = TaskService.get_user_tasks(
        session=session,
        current_user=current_user,
        status=status_filter,
        priority=priority,
        is_favorite=is_favorite,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset
    )
    return TaskListResponse(tasks=tasks, total=total)


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Create a new task for the authenticated user"""
    task = TaskService.create_task(
        session=session,
        task_data=task_data,
        current_user=current_user
    )
    return task


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Get a specific task by ID

    Returns 404 if task not found or not owned by current user
    """
    task = TaskService.get_task_by_id(
        session=session,
        task_id=task_id,
        current_user=current_user
    )
    return task


@router.put("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Update a task

    Returns 404 if task not found or not owned by current user
    """
    task = TaskService.update_task(
        session=session,
        task_id=task_id,
        task_data=task_data,
        current_user=current_user
    )
    return task


@router.patch("/{task_id}/favorite", response_model=TaskRead)
async def toggle_favorite(
    task_id: UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Toggle favorite status of a task"""
    task = TaskService.get_task_by_id(
        session=session,
        task_id=task_id,
        current_user=current_user
    )
    # Toggle favorite status
    updated_task = TaskService.update_task(
        session=session,
        task_id=task_id,
        task_data=TaskUpdate(is_favorite=not task.is_favorite),
        current_user=current_user
    )
    return updated_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Delete a task

    Returns 404 if task not found or not owned by current user
    """
    TaskService.delete_task(
        session=session,
        task_id=task_id,
        current_user=current_user
    )
    return None
