"""Kafka consumer for all task events in audit service"""
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


class AuditEventConsumer:
    """Consumer for all task events from Kafka for audit logging"""

    def __init__(
        self,
        bootstrap_servers: str = "kafka:9092",
        topic: str = "task-events",
        group_id: str = "audit-service-group"
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
        logger.info(f"Audit service consumer started, listening to topic: {self.topic}")

    async def stop(self):
        """Stop the Kafka consumer"""
        self.running = False
        if self.consumer:
            await self.consumer.stop()
        logger.info("Audit service consumer stopped")

    async def process_event(self, event: Dict[str, Any]) -> bool:
        """Process a task event for audit logging

        Args:
            event: Task event data

        Returns:
            True if processing succeeded, False otherwise
        """
        try:
            event_type = event.get('event_type')
            event_id = event.get('event_id')
            user_id = event.get('user_id')
            task_id = event.get('task_id')
            timestamp = event.get('timestamp')

            logger.info(f"Processing event {event_id}: {event_type} for task {task_id}")

            # Import here to avoid circular dependencies
            from .logger import write_audit_log

            # Determine operation type from event type
            operation_map = {
                'task.created': 'CREATE',
                'task.updated': 'UPDATE',
                'task.completed': 'COMPLETE',
                'task.deleted': 'DELETE'
            }
            operation = operation_map.get(event_type, 'UNKNOWN')

            # Extract changes based on event type
            changes = {}
            if event_type == 'task.created':
                changes = event.get('task_data', {})
            elif event_type == 'task.updated':
                changes = {
                    'old': event.get('old_data', {}),
                    'new': event.get('new_data', {})
                }
            elif event_type == 'task.deleted':
                changes = event.get('task_data', {})

            # Write audit log
            await write_audit_log(
                user_id=user_id,
                task_id=task_id,
                operation=operation,
                changes=changes,
                event_id=event_id,
                timestamp=timestamp,
                request_id=event.get('request_id')
            )

            logger.info(f"Wrote audit log for event {event_id}")
            return True

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
    """Main entry point for the audit service consumer"""
    consumer = AuditEventConsumer()
    await consumer.start()

    try:
        await consumer.consume()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(main())
