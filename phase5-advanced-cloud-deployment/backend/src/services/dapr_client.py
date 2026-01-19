"""Dapr client wrapper for pub/sub and state management"""
import os
import json
import time
from typing import Any, Dict, Optional
from dapr.clients import DaprClient
from dapr.clients.grpc._response import TopicEventResponse
from grpc import RpcError
import logging

logger = logging.getLogger(__name__)


class DaprClientWrapper:
    """Wrapper for Dapr SDK client with simplified pub/sub and state operations

    This wrapper abstracts Dapr operations for:
    - Publishing events to Kafka topics via Dapr pub/sub
    - Subscribing to Kafka topics
    - State management via PostgreSQL state store
    - Secret retrieval from Kubernetes secrets

    Features:
    - Connection retry with exponential backoff
    - Automatic reconnection on connection loss
    - Health check for Dapr sidecar availability
    """

    # Retry configuration
    MAX_RETRIES = int(os.getenv("DAPR_MAX_RETRIES", "5"))
    RETRY_DELAY = float(os.getenv("DAPR_RETRY_DELAY", "1.0"))  # seconds
    RETRY_BACKOFF = float(os.getenv("DAPR_RETRY_BACKOFF", "2.0"))  # exponential backoff multiplier

    def __init__(self):
        """Initialize Dapr client with configuration from environment"""
        self.dapr_http_port = os.getenv("DAPR_HTTP_PORT", "3500")
        self.dapr_grpc_port = os.getenv("DAPR_GRPC_PORT", "50001")
        self.pubsub_name = os.getenv("DAPR_PUBSUB_NAME", "pubsub-kafka")
        self.state_store_name = os.getenv("DAPR_STATE_STORE_NAME", "statestore-postgres")
        self.secret_store_name = os.getenv("DAPR_SECRET_STORE_NAME", "secrets-k8s")

        # Initialize Dapr client (uses gRPC by default)
        self._client: Optional[DaprClient] = None
        self._connection_attempts = 0

    def _create_client_with_retry(self) -> DaprClient:
        """
        Create Dapr client with retry logic

        Returns:
            DaprClient instance

        Raises:
            Exception: If connection fails after all retries
        """
        last_error = None
        delay = self.RETRY_DELAY

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                logger.info(f"Attempting to connect to Dapr sidecar (attempt {attempt}/{self.MAX_RETRIES})")

                # Create Dapr client
                client = DaprClient()

                # Test connection by checking Dapr metadata
                try:
                    # Simple health check - try to get metadata
                    metadata = client.get_metadata()
                    logger.info(
                        f"Connected to Dapr sidecar successfully. "
                        f"App ID: {metadata.id}, Runtime version: {metadata.runtime_version}"
                    )
                    self._connection_attempts = attempt
                    return client
                except Exception as e:
                    # Close the client if health check fails
                    client.close()
                    raise e

            except (RpcError, Exception) as e:
                last_error = e
                logger.warning(
                    f"Dapr connection attempt {attempt}/{self.MAX_RETRIES} failed: {e}",
                    extra={"attempt": attempt, "max_retries": self.MAX_RETRIES}
                )

                if attempt < self.MAX_RETRIES:
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= self.RETRY_BACKOFF  # Exponential backoff
                else:
                    logger.error(
                        f"Failed to connect to Dapr sidecar after {self.MAX_RETRIES} attempts. "
                        "Ensure Dapr sidecar is running.",
                        exc_info=True
                    )

        # All retries exhausted
        raise ConnectionError(
            f"Failed to connect to Dapr sidecar after {self.MAX_RETRIES} attempts. "
            f"Last error: {last_error}"
        )

    @property
    def client(self) -> DaprClient:
        """
        Lazy initialization of Dapr client with automatic reconnection

        Returns:
            DaprClient instance

        Raises:
            ConnectionError: If unable to connect to Dapr sidecar
        """
        if self._client is None:
            self._client = self._create_client_with_retry()
        return self._client

    def reconnect(self) -> None:
        """Force reconnection to Dapr sidecar"""
        logger.info("Forcing Dapr client reconnection")
        if self._client is not None:
            try:
                self._client.close()
            except Exception as e:
                logger.warning(f"Error closing existing Dapr client: {e}")
        self._client = None
        # Next access to self.client will trigger reconnection

    async def publish_event(
        self,
        topic: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None
    ) -> None:
        """Publish event to Kafka topic via Dapr pub/sub

        Args:
            topic: Kafka topic name (e.g., 'task-events', 'reminders')
            data: Event data as dictionary
            metadata: Optional metadata for the event

        Raises:
            Exception: If publishing fails
        """
        try:
            # Serialize data to JSON
            event_data = json.dumps(data)

            # Publish via Dapr pub/sub component
            self.client.publish_event(
                pubsub_name=self.pubsub_name,
                topic_name=topic,
                data=event_data,
                data_content_type="application/json",
                metadata=metadata or {}
            )

            logger.info(f"Published event to topic '{topic}': {data.get('event_type', 'unknown')}")

        except Exception as e:
            logger.error(f"Failed to publish event to topic '{topic}': {str(e)}")
            raise

    async def get_state(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve state from PostgreSQL state store via Dapr

        Args:
            key: State key

        Returns:
            State value as dictionary, or None if not found
        """
        try:
            response = self.client.get_state(
                store_name=self.state_store_name,
                key=key
            )

            if response.data:
                return json.loads(response.data)
            return None

        except Exception as e:
            logger.error(f"Failed to get state for key '{key}': {str(e)}")
            return None

    async def save_state(self, key: str, value: Dict[str, Any]) -> None:
        """Save state to PostgreSQL state store via Dapr

        Args:
            key: State key
            value: State value as dictionary
        """
        try:
            state_data = json.dumps(value)

            self.client.save_state(
                store_name=self.state_store_name,
                key=key,
                value=state_data
            )

            logger.info(f"Saved state for key '{key}'")

        except Exception as e:
            logger.error(f"Failed to save state for key '{key}': {str(e)}")
            raise

    async def delete_state(self, key: str) -> None:
        """Delete state from PostgreSQL state store via Dapr

        Args:
            key: State key
        """
        try:
            self.client.delete_state(
                store_name=self.state_store_name,
                key=key
            )

            logger.info(f"Deleted state for key '{key}'")

        except Exception as e:
            logger.error(f"Failed to delete state for key '{key}': {str(e)}")
            raise

    async def get_secret(self, secret_name: str, key: str) -> Optional[str]:
        """Retrieve secret from Kubernetes secrets via Dapr

        Args:
            secret_name: Name of the Kubernetes secret
            key: Key within the secret

        Returns:
            Secret value as string, or None if not found
        """
        try:
            response = self.client.get_secret(
                store_name=self.secret_store_name,
                key=secret_name
            )

            if response.secret:
                return response.secret.get(key)
            return None

        except Exception as e:
            logger.error(f"Failed to get secret '{secret_name}.{key}': {str(e)}")
            return None

    def close(self) -> None:
        """Close Dapr client connection"""
        if self._client is not None:
            self._client.close()
            self._client = None
            logger.info("Dapr client closed")


# Global Dapr client instance
dapr_client = DaprClientWrapper()
