"""WebSocket broadcast service consuming task-updates topic"""
import asyncio
import json
import logging
from typing import Dict, Any
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebSocketBroadcastService:
    """Service that consumes task-updates topic and broadcasts to WebSocket clients"""

    def __init__(
        self,
        bootstrap_servers: str = "kafka:9092",
        topic: str = "task-updates",
        group_id: str = "websocket-broadcast-group"
    ):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.group_id = group_id
        self.consumer = None
        self.running = False
        self.connection_manager = None

    def set_connection_manager(self, manager):
        """Set the WebSocket connection manager

        Args:
            manager: ConnectionManager instance from websocket.py
        """
        self.connection_manager = manager

    async def start(self):
        """Start the Kafka consumer"""
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            enable_auto_commit=True,
            auto_offset_reset='latest'  # Only process new messages
        )
        await self.consumer.start()
        self.running = True
        logger.info(f"WebSocket broadcast service started, listening to topic: {self.topic}")

    async def stop(self):
        """Stop the Kafka consumer"""
        self.running = False
        if self.consumer:
            await self.consumer.stop()
        logger.info("WebSocket broadcast service stopped")

    async def process_event(self, event: Dict[str, Any]) -> bool:
        """Process a task update event and broadcast to WebSocket clients

        Args:
            event: Task update event data

        Returns:
            True if processing succeeded, False otherwise
        """
        try:
            event_type = event.get('event_type')
            user_id = event.get('user_id')
            task_id = event.get('task_id')

            logger.debug(f"Broadcasting event {event_type} for task {task_id} to user {user_id}")

            if not self.connection_manager:
                logger.warning("Connection manager not set, cannot broadcast")
                return True

            # Prepare WebSocket message
            ws_message = {
                "type": "task_update",
                "event_type": event_type,
                "task_id": task_id,
                "timestamp": event.get('timestamp'),
                "data": event.get('task_data', {})
            }

            # Broadcast to specific user's connections
            await self.connection_manager.send_personal_message(ws_message, user_id)

            logger.debug(f"Broadcasted {event_type} to user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error processing event: {str(e)}", exc_info=True)
            return False

    async def consume(self):
        """Main consumer loop"""
        try:
            async for message in self.consumer:
                if not self.running:
                    break

                try:
                    event = message.value
                    await self.process_event(event)

                except Exception as e:
                    logger.error(f"Error in consumer loop: {str(e)}", exc_info=True)
                    await asyncio.sleep(1)

        except KafkaError as e:
            logger.error(f"Kafka error: {str(e)}", exc_info=True)
        finally:
            await self.stop()


# Global broadcast service instance
broadcast_service = WebSocketBroadcastService()


async def start_broadcast_service(connection_manager):
    """Start the WebSocket broadcast service

    Args:
        connection_manager: ConnectionManager instance from websocket.py
    """
    broadcast_service.set_connection_manager(connection_manager)
    await broadcast_service.start()

    # Run consumer in background
    asyncio.create_task(broadcast_service.consume())
    logger.info("WebSocket broadcast service started in background")


async def stop_broadcast_service():
    """Stop the WebSocket broadcast service"""
    await broadcast_service.stop()
