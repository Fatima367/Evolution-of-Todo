"""Event publisher service for task operations"""
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID
import logging

from .dapr_client import dapr_client

logger = logging.getLogger(__name__)


class EventPublisher:
    """Service for publishing task events to Kafka via Dapr

    This service publishes events for all task operations:
    - task.created: When a new task is created
    - task.updated: When a task is modified
    - task.completed: When a task is marked as complete
    - task.deleted: When a task is deleted

    Events are published to Kafka topics:
    - task-events: All task CRUD operations
    - task-updates: Real-time updates for WebSocket broadcast
    - reminders: Scheduled reminder notifications

    Event Reliability Features:
    - Event ordering: Guaranteed by partitioning on user_id
    - At-least-once delivery: Consumers use manual commit with retry logic
    - Error handling: Failed events are logged and can be sent to dead letter queue
    """

    # Kafka topic names
    TOPIC_TASK_EVENTS = "task-events"
    TOPIC_TASK_UPDATES = "task-updates"
    TOPIC_REMINDERS = "reminders"
    TOPIC_DEAD_LETTER = "dead-letter-queue"

    # Retry configuration
    MAX_RETRY_ATTEMPTS = 3
    RETRY_DELAY_MS = 1000

    @staticmethod
    async def _publish_with_retry(
        topic: str,
        data: Dict[str, Any],
        metadata: Dict[str, str],
        max_retries: int = MAX_RETRY_ATTEMPTS
    ) -> bool:
        """Publish event with retry logic

        Args:
            topic: Kafka topic name
            data: Event data
            metadata: Event metadata (includes user_id for partitioning)
            max_retries: Maximum number of retry attempts

        Returns:
            True if published successfully, False otherwise
        """
        for attempt in range(max_retries):
            try:
                await dapr_client.publish_event(
                    topic=topic,
                    data=data,
                    metadata=metadata
                )
                return True
            except Exception as e:
                logger.warning(
                    f"Failed to publish to {topic} (attempt {attempt + 1}/{max_retries}): {str(e)}"
                )
                if attempt == max_retries - 1:
                    # Last attempt failed, send to dead letter queue
                    await EventPublisher._send_to_dead_letter_queue(topic, data, str(e))
                    return False
                # Wait before retry (exponential backoff)
                import asyncio
                await asyncio.sleep((2 ** attempt) * (EventPublisher.RETRY_DELAY_MS / 1000))

        return False

    @staticmethod
    async def _send_to_dead_letter_queue(
        original_topic: str,
        event_data: Dict[str, Any],
        error_message: str
    ) -> None:
        """Send failed event to dead letter queue

        Args:
            original_topic: Original topic where event failed to publish
            event_data: Original event data
            error_message: Error message from failed publish attempt
        """
        try:
            dlq_event = {
                "dlq_id": str(uuid.uuid4()),
                "original_topic": original_topic,
                "original_event": event_data,
                "error_message": error_message,
                "failed_at": datetime.utcnow().isoformat(),
                "retry_count": EventPublisher.MAX_RETRY_ATTEMPTS
            }

            await dapr_client.publish_event(
                topic=EventPublisher.TOPIC_DEAD_LETTER,
                data=dlq_event,
                metadata={"source": "event_publisher"}
            )

            logger.error(
                f"Sent event to dead letter queue. Original topic: {original_topic}, "
                f"Event ID: {event_data.get('event_id')}"
            )
        except Exception as e:
            logger.critical(
                f"Failed to send event to dead letter queue: {str(e)}. "
                f"Original event: {event_data.get('event_id')}"
            )

    @staticmethod
    async def publish_task_created(
        task_id: UUID,
        user_id: UUID,
        task_data: Dict[str, Any],
        request_id: Optional[str] = None
    ) -> None:
        """Publish task.created event

        Args:
            task_id: Task UUID
            user_id: User UUID
            task_data: Complete task data
            request_id: Optional request ID for tracing
        """
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": "task.created",
            "task_id": str(task_id),
            "user_id": str(user_id),
            "timestamp": datetime.utcnow().isoformat(),
            "task_data": task_data,
            "request_id": request_id
        }

        metadata = {"user_id": str(user_id)}  # Partition by user_id

        # Publish to task-events topic for audit service with retry
        success1 = await EventPublisher._publish_with_retry(
            topic=EventPublisher.TOPIC_TASK_EVENTS,
            data=event,
            metadata=metadata
        )

        # Publish to task-updates topic for real-time WebSocket broadcast with retry
        update_event = {
            "event_id": event["event_id"],
            "event_type": "task.changed",
            "task_id": str(task_id),
            "user_id": str(user_id),
            "timestamp": event["timestamp"],
            "operation": "created",
            "task_data": task_data
        }
        success2 = await EventPublisher._publish_with_retry(
            topic=EventPublisher.TOPIC_TASK_UPDATES,
            data=update_event,
            metadata=metadata
        )

        if success1 and success2:
            logger.info(f"Published task.created event for task {task_id}")
        else:
            logger.warning(f"Partial failure publishing task.created event for task {task_id}")

    @staticmethod
    async def publish_task_updated(
        task_id: UUID,
        user_id: UUID,
        task_data: Dict[str, Any],
        changes: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ) -> None:
        """Publish task.updated event

        Args:
            task_id: Task UUID
            user_id: User UUID
            task_data: Complete updated task data
            changes: Dictionary of changed fields (old/new values)
            request_id: Optional request ID for tracing
        """
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": "task.updated",
            "task_id": str(task_id),
            "user_id": str(user_id),
            "timestamp": datetime.utcnow().isoformat(),
            "task_data": task_data,
            "changes": changes or {},
            "request_id": request_id
        }

        metadata = {"user_id": str(user_id)}  # Partition by user_id

        # Publish to task-events topic with retry
        success1 = await EventPublisher._publish_with_retry(
            topic=EventPublisher.TOPIC_TASK_EVENTS,
            data=event,
            metadata=metadata
        )

        # Publish to task-updates topic with retry
        update_event = {
            "event_id": event["event_id"],
            "event_type": "task.changed",
            "task_id": str(task_id),
            "user_id": str(user_id),
            "timestamp": event["timestamp"],
            "operation": "updated",
            "task_data": task_data
        }
        success2 = await EventPublisher._publish_with_retry(
            topic=EventPublisher.TOPIC_TASK_UPDATES,
            data=update_event,
            metadata=metadata
        )

        if success1 and success2:
            logger.info(f"Published task.updated event for task {task_id}")
        else:
            logger.warning(f"Partial failure publishing task.updated event for task {task_id}")

    @staticmethod
    async def publish_task_completed(
        task_id: UUID,
        user_id: UUID,
        task_data: Dict[str, Any],
        request_id: Optional[str] = None
    ) -> None:
        """Publish task.completed event

        Args:
            task_id: Task UUID
            user_id: User UUID
            task_data: Complete task data
            request_id: Optional request ID for tracing
        """
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": "task.completed",
            "task_id": str(task_id),
            "user_id": str(user_id),
            "timestamp": datetime.utcnow().isoformat(),
            "task_data": task_data,
            "request_id": request_id
        }

        metadata = {"user_id": str(user_id)}  # Partition by user_id

        # Publish to task-events topic with retry
        success1 = await EventPublisher._publish_with_retry(
            topic=EventPublisher.TOPIC_TASK_EVENTS,
            data=event,
            metadata=metadata
        )

        # Publish to task-updates topic with retry
        update_event = {
            "event_id": event["event_id"],
            "event_type": "task.changed",
            "task_id": str(task_id),
            "user_id": str(user_id),
            "timestamp": event["timestamp"],
            "operation": "completed",
            "task_data": task_data
        }
        success2 = await EventPublisher._publish_with_retry(
            topic=EventPublisher.TOPIC_TASK_UPDATES,
            data=update_event,
            metadata=metadata
        )

        if success1 and success2:
            logger.info(f"Published task.completed event for task {task_id}")
        else:
            logger.warning(f"Partial failure publishing task.completed event for task {task_id}")

    @staticmethod
    async def publish_task_deleted(
        task_id: UUID,
        user_id: UUID,
        task_data: Dict[str, Any],
        request_id: Optional[str] = None
    ) -> None:
        """Publish task.deleted event

        Args:
            task_id: Task UUID
            user_id: User UUID
            task_data: Task data before deletion
            request_id: Optional request ID for tracing
        """
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": "task.deleted",
            "task_id": str(task_id),
            "user_id": str(user_id),
            "timestamp": datetime.utcnow().isoformat(),
            "task_data": task_data,
            "request_id": request_id
        }

        metadata = {"user_id": str(user_id)}  # Partition by user_id

        # Publish to task-events topic with retry
        success1 = await EventPublisher._publish_with_retry(
            topic=EventPublisher.TOPIC_TASK_EVENTS,
            data=event,
            metadata=metadata
        )

        # Publish to task-updates topic with retry
        update_event = {
            "event_id": event["event_id"],
            "event_type": "task.changed",
            "task_id": str(task_id),
            "user_id": str(user_id),
            "timestamp": event["timestamp"],
            "operation": "deleted",
            "task_data": task_data
        }
        success2 = await EventPublisher._publish_with_retry(
            topic=EventPublisher.TOPIC_TASK_UPDATES,
            data=update_event,
            metadata=metadata
        )

        if success1 and success2:
            logger.info(f"Published task.deleted event for task {task_id}")
        else:
            logger.warning(f"Partial failure publishing task.deleted event for task {task_id}")

    @staticmethod
    async def publish_reminder_due(
        reminder_id: int,
        task_id: UUID,
        user_id: UUID,
        task_data: Dict[str, Any],
        request_id: Optional[str] = None
    ) -> None:
        """Publish reminder.due event

        Args:
            reminder_id: Reminder ID
            task_id: Task UUID
            user_id: User UUID
            task_data: Task data for the reminder
            request_id: Optional request ID for tracing
        """
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": "reminder.due",
            "reminder_id": reminder_id,
            "task_id": str(task_id),
            "user_id": str(user_id),
            "timestamp": datetime.utcnow().isoformat(),
            "task_data": {
                "title": task_data.get("title"),
                "due_date": task_data.get("due_date")
            },
            "request_id": request_id
        }

        metadata = {"user_id": str(user_id)}  # Partition by user_id

        # Publish to reminders topic for notification service with retry
        success = await EventPublisher._publish_with_retry(
            topic=EventPublisher.TOPIC_REMINDERS,
            data=event,
            metadata=metadata
        )

        if success:
            logger.info(f"Published reminder.due event for task {task_id}")
        else:
            logger.warning(f"Failed to publish reminder.due event for task {task_id}")


# Global event publisher instance
event_publisher = EventPublisher()
