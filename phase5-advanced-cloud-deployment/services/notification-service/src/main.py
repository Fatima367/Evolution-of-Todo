"""Notification Service - Handles reminder notifications via Kafka/Dapr

This service:
- Subscribes to 'reminders' topic via Dapr
- Sends notifications when reminders are due
- Logs notification events for audit trail
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
SERVICE_NAME = os.getenv("SERVICE_NAME", "notification-service")
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
    title="TodoBoard Notification Service",
    description="Handles reminder notifications for tasks",
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
            "events": "/events/reminders"
        }
    }


@app.post("/events/reminders")
async def handle_reminder_event(request: Request):
    """Handle reminder events from Kafka via Dapr

    Event schema:
    {
        "task_id": "uuid",
        "user_id": "uuid",
        "title": "Task title",
        "due_at": "2024-01-20T10:00:00Z",
        "remind_at": "2024-01-20T09:45:00Z"
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

        logger.info(f"Received reminder event: {json.dumps(data, default=str)}")

        # Extract reminder details
        task_id = data.get("task_id")
        user_id = data.get("user_id")
        title = data.get("title", "Untitled Task")
        due_at = data.get("due_at")
        remind_at = data.get("remind_at")

        # Validate required fields
        if not all([task_id, user_id, due_at]):
            logger.error(f"Missing required fields in reminder event: {data}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Missing required fields"}
            )

        # Send notification (in production, this would integrate with email/SMS/push services)
        notification_sent = await send_notification(
            user_id=user_id,
            task_id=task_id,
            title=title,
            due_at=due_at,
            remind_at=remind_at
        )

        if notification_sent:
            logger.info(f"Notification sent successfully for task {task_id}")

            # Publish notification.sent event
            await publish_notification_sent_event(
                task_id=task_id,
                user_id=user_id,
                notification_type="reminder"
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"status": "success", "message": "Notification sent"}
            )
        else:
            logger.error(f"Failed to send notification for task {task_id}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "Failed to send notification"}
            )

    except Exception as e:
        logger.error(f"Error processing reminder event: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(e)}
        )


async def send_notification(
    user_id: str,
    task_id: str,
    title: str,
    due_at: str,
    remind_at: str
) -> bool:
    """Send notification to user

    In production, this would integrate with:
    - Email service (SendGrid, AWS SES)
    - SMS service (Twilio)
    - Push notification service (Firebase, OneSignal)
    - In-app notifications

    For now, we log the notification.
    """
    try:
        notification_message = (
            f"⏰ Reminder: '{title}' is due at {due_at}. "
            f"Don't forget to complete it!"
        )

        logger.info(
            f"📧 NOTIFICATION SENT:\n"
            f"  User ID: {user_id}\n"
            f"  Task ID: {task_id}\n"
            f"  Message: {notification_message}\n"
            f"  Remind At: {remind_at}"
        )

        # TODO: Integrate with actual notification service
        # Example:
        # await send_email(user_id, "Task Reminder", notification_message)
        # await send_push_notification(user_id, notification_message)

        return True

    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        return False


async def publish_notification_sent_event(
    task_id: str,
    user_id: str,
    notification_type: str
):
    """Publish notification.sent event to Kafka via Dapr"""
    try:
        event_data = {
            "event_type": "notification.sent",
            "task_id": task_id,
            "user_id": user_id,
            "notification_type": notification_type,
            "sent_at": datetime.utcnow().isoformat(),
            "service": SERVICE_NAME
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{DAPR_PUBSUB_NAME}/task-events",
                json=event_data,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                logger.info(f"Published notification.sent event for task {task_id}")
            else:
                logger.error(
                    f"Failed to publish notification.sent event: "
                    f"{response.status_code} - {response.text}"
                )

    except Exception as e:
        logger.error(f"Error publishing notification.sent event: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8001"))

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
