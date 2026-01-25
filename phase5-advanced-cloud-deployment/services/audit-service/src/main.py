"""Audit Service - Logs all task operations for audit trail via Kafka/Dapr

This service:
- Subscribes to 'task-events' topic via Dapr
- Logs all task CRUD operations (create, update, delete, complete)
- Stores audit logs in database via Dapr state store
- Provides audit trail for compliance and debugging
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any
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
SERVICE_NAME = os.getenv("SERVICE_NAME", "audit-service")
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_PUBSUB_NAME = os.getenv("DAPR_PUBSUB_NAME", "pubsub-kafka")
DAPR_STATE_STORE = os.getenv("DAPR_STATE_STORE", "statestore-postgres")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info(f"{SERVICE_NAME} starting up...")
    yield
    logger.info(f"{SERVICE_NAME} shutting down...")


# Create FastAPI application
app = FastAPI(
    title="TodoBoard Audit Service",
    description="Logs all task operations for audit trail",
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
            "events": "/events/task-events",
            "audit-logs": "/audit-logs/{user_id}"
        }
    }


@app.post("/events/task-events")
async def handle_task_event(request: Request):
    """Handle task events from Kafka via Dapr

    Logs all task operations for audit trail.

    Event schema:
    {
        "event_type": "task.created|task.updated|task.completed|task.deleted",
        "task_id": "uuid",
        "user_id": "uuid",
        "task_data": {...},
        "timestamp": "2024-01-20T10:00:00Z"
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

        logger.info(f"Received task event for audit: {json.dumps(data, default=str)}")

        # Extract event details
        event_type = data.get("event_type")
        task_id = data.get("task_id")
        user_id = data.get("user_id")
        task_data = data.get("task_data", {})
        timestamp = data.get("timestamp", datetime.utcnow().isoformat())

        # Validate required fields
        if not all([event_type, task_id, user_id]):
            logger.error(f"Missing required fields in audit event: {data}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Missing required fields"}
            )

        # Create audit log entry
        audit_log = {
            "audit_id": f"{task_id}_{timestamp}",
            "event_type": event_type,
            "task_id": task_id,
            "user_id": user_id,
            "task_data": task_data,
            "timestamp": timestamp,
            "service": SERVICE_NAME
        }

        # Store audit log
        success = await store_audit_log(audit_log)

        if success:
            logger.info(f"Audit log stored for task {task_id}, event: {event_type}")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"status": "success", "message": "Audit log stored"}
            )
        else:
            logger.error(f"Failed to store audit log for task {task_id}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "Failed to store audit log"}
            )

    except Exception as e:
        logger.error(f"Error processing audit event: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(e)}
        )


async def store_audit_log(audit_log: Dict[str, Any]) -> bool:
    """Store audit log in Dapr state store (PostgreSQL)

    Args:
        audit_log: Audit log entry to store

    Returns:
        True if successful, False otherwise
    """
    try:
        # Generate state key
        state_key = f"audit:{audit_log['user_id']}:{audit_log['audit_id']}"

        # Store in Dapr state store
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://localhost:{DAPR_HTTP_PORT}/v1.0/state/{DAPR_STATE_STORE}",
                json=[{
                    "key": state_key,
                    "value": audit_log
                }],
                headers={"Content-Type": "application/json"}
            )

            if response.status_code in [200, 201, 204]:
                logger.info(f"Audit log stored with key: {state_key}")
                return True
            else:
                logger.error(
                    f"Failed to store audit log: "
                    f"{response.status_code} - {response.text}"
                )
                return False

    except Exception as e:
        logger.error(f"Error storing audit log: {str(e)}")
        return False


@app.get("/audit-logs/{user_id}")
async def get_audit_logs(user_id: str, limit: int = 100):
    """Get audit logs for a specific user

    This is a placeholder endpoint. In production, you would:
    1. Query the state store for all audit logs for the user
    2. Implement pagination
    3. Add filtering by date range, event type, etc.
    """
    try:
        # TODO: Implement actual query logic
        # For now, return a placeholder response
        return {
            "user_id": user_id,
            "message": "Audit log retrieval not yet implemented",
            "note": "Audit logs are stored in Dapr state store (PostgreSQL)"
        }

    except Exception as e:
        logger.error(f"Error retrieving audit logs: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(e)}
        )


@app.get("/stats")
async def get_audit_stats():
    """Get audit statistics

    Returns statistics about audit logs processed.
    """
    return {
        "service": SERVICE_NAME,
        "status": "operational",
        "message": "Audit statistics not yet implemented"
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8003"))

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
