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
async def get_audit_logs(
    user_id: str,
    limit: int = 100,
    offset: int = 0,
    event_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get audit logs for a specific user

    Args:
        user_id: User ID to retrieve logs for
        limit: Maximum number of logs to return (default: 100)
        offset: Number of logs to skip for pagination (default: 0)
        event_type: Filter by event type (e.g., 'task.created', 'task.updated')
        start_date: Filter logs after this date (ISO format)
        end_date: Filter logs before this date (ISO format)

    Returns:
        List of audit logs with pagination metadata

    Note: This implementation uses Dapr state store query API.
    For production with high volume, consider using a dedicated audit log database
    or time-series database like InfluxDB or TimescaleDB.
    """
    try:
        # Build query for Dapr state store
        # Note: This uses Dapr's query API which requires the state store to support querying
        # PostgreSQL state store supports this via SQL queries
        query = {
            "filter": {
                "AND": [
                    {
                        "EQ": {"user_id": user_id}
                    }
                ]
            },
            "sort": [
                {
                    "key": "timestamp",
                    "order": "DESC"
                }
            ],
            "page": {
                "limit": limit,
                "token": str(offset) if offset > 0 else ""
            }
        }

        # Add event type filter if provided
        if event_type:
            query["filter"]["AND"].append({
                "EQ": {"event_type": event_type}
            })

        # Add date range filters if provided
        if start_date:
            query["filter"]["AND"].append({
                "GTE": {"timestamp": start_date}
            })
        if end_date:
            query["filter"]["AND"].append({
                "LTE": {"timestamp": end_date}
            })

        # Query Dapr state store
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://localhost:{DAPR_HTTP_PORT}/v1.0-alpha1/state/{DAPR_STATE_STORE}/query",
                json=query,
                headers={"Content-Type": "application/json"},
                timeout=10.0
            )

            if response.status_code == 200:
                result = response.json()
                logs = result.get("results", [])

                # Extract audit log data from results
                audit_logs = []
                for item in logs:
                    if "data" in item:
                        audit_logs.append(item["data"])

                logger.info(f"Retrieved {len(audit_logs)} audit logs for user {user_id}")

                return {
                    "user_id": user_id,
                    "logs": audit_logs,
                    "count": len(audit_logs),
                    "limit": limit,
                    "offset": offset,
                    "has_more": len(audit_logs) == limit,
                    "filters": {
                        "event_type": event_type,
                        "start_date": start_date,
                        "end_date": end_date
                    }
                }
            elif response.status_code == 501:
                # Query API not supported by state store
                logger.warning(
                    f"State store query API not supported. "
                    f"Falling back to basic retrieval."
                )
                return {
                    "user_id": user_id,
                    "message": "Query API not supported by state store",
                    "note": "Audit logs are stored but cannot be queried. "
                            "Consider using a state store that supports querying (e.g., PostgreSQL, MongoDB) "
                            "or implement a dedicated audit log service with a time-series database.",
                    "logs": [],
                    "count": 0
                }
            else:
                logger.error(
                    f"Failed to query audit logs: "
                    f"{response.status_code} - {response.text}"
                )
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={
                        "error": "Failed to retrieve audit logs",
                        "details": response.text
                    }
                )

    except httpx.TimeoutException:
        logger.error(f"Timeout querying audit logs for user {user_id}")
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={"error": "Request timeout while retrieving audit logs"}
        )
    except Exception as e:
        logger.error(f"Error retrieving audit logs: {str(e)}", exc_info=True)
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
