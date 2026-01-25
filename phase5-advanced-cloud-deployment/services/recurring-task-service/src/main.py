"""Recurring Task Service - Handles recurring task generation via Kafka/Dapr

This service:
- Subscribes to 'task-events' topic via Dapr
- Listens for 'task.completed' events for recurring tasks
- Automatically creates next occurrence based on recurrence pattern
- Publishes 'task.created' events for new occurrences
"""
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment variables
SERVICE_NAME = os.getenv("SERVICE_NAME", "recurring-task-service")
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_PUBSUB_NAME = os.getenv("DAPR_PUBSUB_NAME", "pubsub-kafka")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info(f"{SERVICE_NAME} starting up...")
    yield
    logger.info(f"{SERVICE_NAME} shutting down...")


# Create FastAPI application
app = FastAPI(
    title="TodoBoard Recurring Task Service",
    description="Handles automatic creation of recurring task instances",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes probes"""
    return {
        "status": "healthy",
        "service": SERVICE_NAME,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": SERVICE_NAME,
        "status": "running",
        "endpoints": {
            "health": "/health",
            "events": "/events/task-events"
        }
    }


@app.post("/events/task-events")
async def handle_task_event(request: Request):
    """Handle task events from Kafka via Dapr

    Listens for task.completed events and creates next occurrence for recurring tasks.

    Event schema:
    {
        "event_type": "task.completed",
        "task_id": "uuid",
        "user_id": "uuid",
        "task_data": {
            "title": "Task title",
            "recurring_type": "daily|weekly|monthly|yearly",
            "recurring_pattern": {...}
        }
    }
    """
    try:
        # Parse event data
        event_data = await request.json()

        # Extract CloudEvents data if present
        if "data" in event_data:
            data = event_data["data"]
        else:
            data = event_data

        logger.info(f"Received task event: {json.dumps(data, default=str)}")

        # Extract event details
        event_type = data.get("event_type")
        task_id = data.get("task_id")
        user_id = data.get("user_id")
        task_data = data.get("task_data", {})

        # Only process task.completed events
        if event_type != "task.completed":
            logger.debug(f"Ignoring event type: {event_type}")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"status": "ignored", "reason": "Not a task.completed event"}
            )

        # Check if task is recurring
        recurring_type = task_data.get("recurring_type", "none")
        if recurring_type == "none":
            logger.debug(f"Task {task_id} is not recurring, skipping")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"status": "ignored", "reason": "Not a recurring task"}
            )

        # Calculate next occurrence
        next_task_data = calculate_next_occurrence(task_data, recurring_type)

        if next_task_data:
            # Create next task instance
            success = await create_next_task_instance(
                user_id=user_id,
                original_task_id=task_id,
                next_task_data=next_task_data
            )

            if success:
                logger.info(f"Created next occurrence for recurring task {task_id}")
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"status": "success", "message": "Next occurrence created"}
                )
            else:
                logger.error(f"Failed to create next occurrence for task {task_id}")
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={"error": "Failed to create next occurrence"}
                )
        else:
            logger.info(f"No next occurrence needed for task {task_id}")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"status": "success", "message": "No next occurrence needed"}
            )

    except Exception as e:
        logger.error(f"Error processing task event: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(e)}
        )


def calculate_next_occurrence(task_data: Dict[str, Any], recurring_type: str) -> Optional[Dict[str, Any]]:
    """Calculate next occurrence based on recurring pattern

    Args:
        task_data: Original task data
        recurring_type: Type of recurrence (daily, weekly, monthly, yearly)

    Returns:
        Dictionary with next task data, or None if no next occurrence
    """
    try:
        # Get current due date or use current time
        due_date_str = task_data.get("due_date")
        if due_date_str:
            current_due = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
        else:
            current_due = datetime.utcnow()

        # Calculate next due date based on recurring type
        if recurring_type == "daily":
            next_due = current_due + timedelta(days=1)
        elif recurring_type == "weekly":
            next_due = current_due + timedelta(weeks=1)
        elif recurring_type == "monthly":
            # Add one month (approximate)
            next_due = current_due + timedelta(days=30)
        elif recurring_type == "yearly":
            next_due = current_due + timedelta(days=365)
        else:
            logger.warning(f"Unknown recurring type: {recurring_type}")
            return None

        # Create next task data
        next_task_data = {
            "title": task_data.get("title"),
            "description": task_data.get("description"),
            "priority": task_data.get("priority", "medium"),
            "due_date": next_due.isoformat(),
            "tags": task_data.get("tags", []),
            "recurring_type": recurring_type,
            "status": "pending"
        }

        logger.info(f"Calculated next occurrence: {next_due.isoformat()}")
        return next_task_data

    except Exception as e:
        logger.error(f"Error calculating next occurrence: {str(e)}")
        return None


async def create_next_task_instance(
    user_id: str,
    original_task_id: str,
    next_task_data: Dict[str, Any]
) -> bool:
    """Create next task instance by publishing task.created event

    In production, this would call the backend API to create the task.
    For now, we publish an event that the backend can consume.
    """
    try:
        event_data = {
            "event_type": "recurring.task.created",
            "user_id": user_id,
            "original_task_id": original_task_id,
            "task_data": next_task_data,
            "created_at": datetime.utcnow().isoformat(),
            "service": SERVICE_NAME
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{DAPR_PUBSUB_NAME}/task-events",
                json=event_data,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                logger.info(f"Published recurring.task.created event for user {user_id}")
                return True
            else:
                logger.error(
                    f"Failed to publish recurring.task.created event: "
                    f"{response.status_code} - {response.text}"
                )
                return False

    except Exception as e:
        logger.error(f"Error creating next task instance: {str(e)}")
        return False


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8002"))

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
