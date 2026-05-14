"""Task management API endpoints"""
from typing import Annotated, Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session
from src.database import get_session
from src.auth.dependencies import get_current_user
from src.models.user import User
from src.models.task import TaskStatus, TaskPriority
from src.schemas.task_schemas import TaskCreate, TaskRead, TaskUpdate, TaskListResponse, SortField, SortOrder
from src.services.task_service import TaskService
from src.services.event_publisher import EventPublisher


router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/", response_model=TaskListResponse)
async def get_tasks(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    status_filter: Optional[TaskStatus] = Query(None, alias="status", description="Filter by status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by priority"),
    is_favorite: Optional[bool] = Query(None, description="Filter by favorite status"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags (matches if task has ANY of these tags)"),
    search: Optional[str] = Query(None, description="Full-text search in title and description"),
    sort_by: Optional[SortField] = Query(SortField.CREATED_AT, description="Field to sort by"),
    sort_order: Optional[SortOrder] = Query(SortOrder.DESC, description="Sort direction"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of tasks"),
    offset: int = Query(0, ge=0, description="Number of tasks to skip")
):
    """Get all tasks for the authenticated user with optional filtering, searching, and sorting

    Enforces user isolation by filtering tasks by current_user.id

    Supports:
    - Status, priority, favorite filtering
    - Tag filtering (OR logic - matches if task has ANY of the provided tags)
    - Full-text search on title and description
    - Sorting by created_at, due_date, priority, or title
    """
    tasks, total = TaskService.get_user_tasks(
        session=session,
        current_user=current_user,
        status=status_filter,
        priority=priority,
        is_favorite=is_favorite,
        tags=tags,
        search_query=search,
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

    # Publish task.created event
    await EventPublisher.publish_task_created(
        task_id=task.id,
        user_id=current_user.id,
        task_data={
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "status": task.status,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "tags": task.tags,
            "is_favorite": task.is_favorite,
            "recurring_type": task.recurring_type,
        }
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
    # Get old task state for comparison
    old_task = TaskService.get_task_by_id(
        session=session,
        task_id=task_id,
        current_user=current_user
    )

    task = TaskService.update_task(
        session=session,
        task_id=task_id,
        task_data=task_data,
        current_user=current_user
    )

    # Publish task.updated event
    await EventPublisher.publish_task_updated(
        task_id=task.id,
        user_id=current_user.id,
        old_data={
            "title": old_task.title,
            "description": old_task.description,
            "priority": old_task.priority,
            "status": old_task.status,
            "due_date": old_task.due_date.isoformat() if old_task.due_date else None,
            "tags": old_task.tags,
            "is_favorite": old_task.is_favorite,
            "recurring_type": old_task.recurring_type,
        },
        new_data={
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "status": task.status,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "tags": task.tags,
            "is_favorite": task.is_favorite,
            "recurring_type": task.recurring_type,
        }
    )

    # If task was completed, publish task.completed event
    if old_task.status != TaskStatus.COMPLETED and task.status == TaskStatus.COMPLETED:
        await EventPublisher.publish_task_completed(
            task_id=task.id,
            user_id=current_user.id,
            task_data={
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "tags": task.tags,
                "recurring_type": task.recurring_type,
            }
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
    # Get task before deletion for event data
    task = TaskService.get_task_by_id(
        session=session,
        task_id=task_id,
        current_user=current_user
    )

    TaskService.delete_task(
        session=session,
        task_id=task_id,
        current_user=current_user
    )

    # Publish task.deleted event
    await EventPublisher.publish_task_deleted(
        task_id=task_id,
        user_id=current_user.id,
        task_data={
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "status": task.status,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "tags": task.tags,
            "is_favorite": task.is_favorite,
            "recurring_type": task.recurring_type,
        }
    )

    return None
