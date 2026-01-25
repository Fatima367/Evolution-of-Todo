"""Event Publisher Service - Publishes task events to Kafka via Dapr

This service provides a centralized interface for publishing task-related events
to Kafka topics via Dapr pub/sub component.
"""
import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)

# Environment variables
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_PUBSUB_NAME = os.getenv("DAPR_PUBSUB_NAME", "pubsub-kafka")


class EventPublisher:
    """Centralized event publisher for task-related events"""

    @staticmethod
    async def publish_event(
        topic: str,
        event_type: str,
        task_id: str,
        user_id: str,
        task_data: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """Publish event to Kafka via Dapr

        Args:
            topic: Kafka topic name (e.g., 'task-events', 'reminders')
            event_type: Type of event (e.g., 'task.created', 'task.updated')
            task_id: Task UUID
            user_id: User UUID
            task_data: Task data dictionary
            metadata: Optional metadata for the event

        Returns:
            True if successful, False otherwise
        """
        try:
            event_data = {
                "event_type": event_type,
                "task_id": str(task_id),
                "user_id": str(user_id),
                "task_data": task_data,
                "timestamp": datetime.utcnow().isoformat(),
                "service": "backend-service"
            }

            # Add metadata if provided
            if metadata:
                event_data["metadata"] = metadata

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{DAPR_PUBSUB_NAME}/{topic}",
                    json=event_data,
                    headers={"Content-Type": "application/json"},
                    timeout=5.0
                )

                if response.status_code in [200, 204]:
                    logger.info(
                        f"Published event: {event_type} for task {task_id} to topic {topic}"
                    )
                    return True
                else:
                    logger.error(
                        f"Failed to publish event: {response.status_code} - {response.text}"
                    )
                    return False

        except httpx.TimeoutException:
            logger.error(f"Timeout publishing event {event_type} for task {task_id}")
            return False
        except Exception as e:
            logger.error(f"Error publishing event: {str(e)}", exc_info=True)
            return False

    @staticmethod
    async def publish_task_created(
        task_id: str,
        user_id: str,
        task_data: Dict[str, Any]
    ) -> bool:
        """Publish task.created event"""
        return await EventPublisher.publish_event(
            topic="task-events",
            event_type="task.created",
            task_id=task_id,
            user_id=user_id,
            task_data=task_data
        )

    @staticmethod
    async def publish_task_updated(
        task_id: str,
        user_id: str,
        task_data: Dict[str, Any]
    ) -> bool:
        """Publish task.updated event"""
        return await EventPublisher.publish_event(
            topic="task-events",
            event_type="task.updated",
            task_id=task_id,
            user_id=user_id,
            task_data=task_data
        )

    @staticmethod
    async def publish_task_completed(
        task_id: str,
        user_id: str,
        task_data: Dict[str, Any]
    ) -> bool:
        """Publish task.completed event"""
        return await EventPublisher.publish_event(
            topic="task-events",
            event_type="task.completed",
            task_id=task_id,
            user_id=user_id,
            task_data=task_data
        )

    @staticmethod
    async def publish_task_deleted(
        task_id: str,
        user_id: str,
        task_data: Dict[str, Any]
    ) -> bool:
        """Publish task.deleted event"""
        return await EventPublisher.publish_event(
            topic="task-events",
            event_type="task.deleted",
            task_id=task_id,
            user_id=user_id,
            task_data=task_data
        )

    @staticmethod
    async def publish_reminder(
        task_id: str,
        user_id: str,
        title: str,
        due_at: str,
        remind_at: str
    ) -> bool:
        """Publish reminder event

        Args:
            task_id: Task UUID
            user_id: User UUID
            title: Task title
            due_at: When task is due (ISO format)
            remind_at: When to send reminder (ISO format)

        Returns:
            True if successful, False otherwise
        """
        try:
            event_data = {
                "task_id": str(task_id),
                "user_id": str(user_id),
                "title": title,
                "due_at": due_at,
                "remind_at": remind_at,
                "timestamp": datetime.utcnow().isoformat(),
                "service": "backend-service"
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{DAPR_PUBSUB_NAME}/reminders",
                    json=event_data,
                    headers={"Content-Type": "application/json"},
                    timeout=5.0
                )

                if response.status_code in [200, 204]:
                    logger.info(f"Published reminder for task {task_id}")
                    return True
                else:
                    logger.error(
                        f"Failed to publish reminder: {response.status_code} - {response.text}"
                    )
                    return False

        except Exception as e:
            logger.error(f"Error publishing reminder: {str(e)}", exc_info=True)
            return False

    @staticmethod
    async def publish_task_update_notification(
        task_id: str,
        user_id: str,
        update_type: str,
        task_data: Dict[str, Any]
    ) -> bool:
        """Publish task update notification for real-time sync

        Args:
            task_id: Task UUID
            user_id: User UUID
            update_type: Type of update (created, updated, deleted, completed)
            task_data: Task data

        Returns:
            True if successful, False otherwise
        """
        return await EventPublisher.publish_event(
            topic="task-updates",
            event_type=f"task.{update_type}",
            task_id=task_id,
            user_id=user_id,
            task_data=task_data
        )
