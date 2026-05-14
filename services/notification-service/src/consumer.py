"""Kafka consumer for reminder events in notification service"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReminderEventConsumer:
    """Consumer for reminder events from Kafka"""

    def __init__(
        self,
        bootstrap_servers: str = "kafka:9092",
        topic: str = "reminders",
        group_id: str = "notification-service-group"
    ):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.group_id = group_id
        self.consumer = None
        self.running = False

    async def start(self):
        """Start the Kafka consumer"""
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            enable_auto_commit=False,  # Manual commit for at-least-once delivery
            auto_offset_reset='earliest'
        )
        await self.consumer.start()
        self.running = True
        logger.info(f"Notification service consumer started, listening to topic: {self.topic}")

    async def stop(self):
        """Stop the Kafka consumer"""
        self.running = False
        if self.consumer:
            await self.consumer.stop()
        logger.info("Notification service consumer stopped")

    async def process_event(self, event: Dict[str, Any]) -> bool:
        """Process a reminder event

        Args:
            event: Reminder event data

        Returns:
            True if processing succeeded, False otherwise
        """
        try:
            event_type = event.get('event_type')
            event_id = event.get('event_id')
            user_id = event.get('user_id')
            reminder_data = event.get('reminder_data', {})

            logger.info(f"Processing event {event_id}: {event_type} for user {user_id}")

            if event_type == 'reminder.due':
                # Import here to avoid circular dependencies
                from .notifier import send_push_notification

                # Send push notification
                await send_push_notification(
                    user_id=user_id,
                    title=reminder_data.get('task_title', 'Task Reminder'),
                    body=reminder_data.get('message', 'You have a task due soon'),
                    data={
                        'task_id': reminder_data.get('task_id'),
                        'remind_at': reminder_data.get('remind_at'),
                        'due_date': reminder_data.get('due_date')
                    }
                )

                logger.info(f"Sent push notification for reminder {event_id}")
                return True

            else:
                logger.warning(f"Unknown event type: {event_type}")
                return True  # Return True to commit offset (skip unknown events)

        except Exception as e:
            logger.error(f"Error processing event {event.get('event_id')}: {str(e)}", exc_info=True)
            return False

    async def consume(self):
        """Main consumer loop"""
        retry_count = 0
        max_retries = 3

        try:
            async for message in self.consumer:
                if not self.running:
                    break

                try:
                    event = message.value
                    success = await self.process_event(event)

                    if success:
                        # Commit offset after successful processing
                        await self.consumer.commit()
                        retry_count = 0
                    else:
                        # Retry logic
                        retry_count += 1
                        if retry_count >= max_retries:
                            logger.error(
                                f"Failed to process event after {max_retries} retries. "
                                f"Moving to next message. Event: {event.get('event_id')}"
                            )
                            # Commit offset to skip this message (dead letter queue would be better)
                            await self.consumer.commit()
                            retry_count = 0
                        else:
                            logger.warning(f"Retrying event processing (attempt {retry_count}/{max_retries})")
                            await asyncio.sleep(2 ** retry_count)  # Exponential backoff

                except Exception as e:
                    logger.error(f"Error in consumer loop: {str(e)}", exc_info=True)
                    await asyncio.sleep(5)

        except KafkaError as e:
            logger.error(f"Kafka error: {str(e)}", exc_info=True)
        finally:
            await self.stop()


async def main():
    """Main entry point for the notification service consumer"""
    consumer = ReminderEventConsumer()
    await consumer.start()

    try:
        await consumer.consume()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(main())
