"""WebSocket endpoint for real-time task updates"""
import logging
from typing import Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from src.auth.dependencies import get_current_user_from_websocket
from src.models.user import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""

    def __init__(self):
        # Map of user_id to set of WebSocket connections
        self.active_connections: dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept a new WebSocket connection

        Args:
            websocket: WebSocket connection
            user_id: User ID
        """
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()

        self.active_connections[user_id].add(websocket)
        logger.info(f"User {user_id} connected. Total connections: {len(self.active_connections[user_id])}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove a WebSocket connection

        Args:
            websocket: WebSocket connection
            user_id: User ID
        """
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)

            # Clean up empty sets
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

            logger.info(f"User {user_id} disconnected. Remaining connections: {len(self.active_connections.get(user_id, []))}")

    async def send_personal_message(self, message: dict, user_id: str):
        """Send a message to all connections for a specific user

        Args:
            message: Message to send
            user_id: User ID
        """
        if user_id not in self.active_connections:
            return

        # Send to all connections for this user
        disconnected = set()
        for connection in self.active_connections[user_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {str(e)}")
                disconnected.add(connection)

        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection, user_id)

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected users

        Args:
            message: Message to broadcast
        """
        for user_id, connections in list(self.active_connections.items()):
            await self.send_personal_message(message, user_id)

    def get_connection_count(self, user_id: str = None) -> int:
        """Get the number of active connections

        Args:
            user_id: Optional user ID to get count for specific user

        Returns:
            Number of active connections
        """
        if user_id:
            return len(self.active_connections.get(user_id, []))
        return sum(len(connections) for connections in self.active_connections.values())


# Global connection manager instance
manager = ConnectionManager()


@router.websocket("/ws/tasks")
async def websocket_endpoint(
    websocket: WebSocket,
    current_user: User = Depends(get_current_user_from_websocket)
):
    """WebSocket endpoint for real-time task updates

    Clients connect to this endpoint to receive real-time updates about their tasks.
    Updates are pushed when tasks are created, updated, or deleted.
    """
    user_id = str(current_user.id)
    await manager.connect(websocket, user_id)

    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        # Keep connection alive and handle incoming messages
        while True:
            # Receive messages from client (e.g., ping/pong for keepalive)
            data = await websocket.receive_json()

            # Handle ping/pong for keepalive
            if data.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        logger.info(f"WebSocket disconnected for user {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {str(e)}", exc_info=True)
        manager.disconnect(websocket, user_id)


# Import datetime for timestamps
from datetime import datetime, timezone
