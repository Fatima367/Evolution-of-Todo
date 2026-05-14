"""Audit log writer for audit service"""
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Backend API configuration
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://backend:8000")
API_TIMEOUT = 30.0

# Audit log retention period (90 days)
RETENTION_DAYS = 90


async def write_audit_log(
    user_id: str,
    task_id: str,
    operation: str,
    changes: Dict[str, Any],
    event_id: str,
    timestamp: str,
    request_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> bool:
    """Write an audit log entry to the database

    Args:
        user_id: User ID who performed the operation
        task_id: Task ID that was affected
        operation: Operation type (CREATE, UPDATE, DELETE, COMPLETE)
        changes: Changes made (JSONB format)
        event_id: Event ID from Kafka
        timestamp: Event timestamp
        request_id: Optional request ID for tracing
        ip_address: Optional IP address of the request
        user_agent: Optional user agent string

    Returns:
        True if written successfully, False otherwise
    """
    try:
        logger.info(f"Writing audit log for {operation} on task {task_id} by user {user_id}")

        # Prepare audit log data
        audit_data = {
            "user_id": user_id,
            "task_id": task_id,
            "operation": operation,
            "changes": changes,
            "event_id": event_id,
            "timestamp": timestamp,
            "request_id": request_id,
            "ip_address": ip_address,
            "user_agent": user_agent
        }

        # Write to database via backend API
        success = await write_audit_log_via_api(audit_data)

        if success:
            logger.info(f"Successfully wrote audit log for event {event_id}")
            return True
        else:
            logger.error(f"Failed to write audit log for event {event_id}")
            return False

    except Exception as e:
        logger.error(f"Error writing audit log for event {event_id}: {str(e)}", exc_info=True)
        return False


async def write_audit_log_via_api(audit_data: Dict[str, Any]) -> bool:
    """Write audit log via backend API

    Args:
        audit_data: Audit log data

    Returns:
        True if written successfully, False otherwise
    """
    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.post(
                f"{BACKEND_API_URL}/audit-logs",
                json=audit_data,
                headers={"X-Service": "audit-service"}  # Service-to-service auth
            )

            if response.status_code in (200, 201):
                return True
            else:
                logger.error(f"Error writing audit log: {response.status_code} - {response.text}")
                return False

    except Exception as e:
        logger.error(f"Error calling backend API: {str(e)}", exc_info=True)
        return False


async def cleanup_old_audit_logs() -> int:
    """Clean up audit logs older than retention period

    Returns:
        Number of logs deleted
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=RETENTION_DAYS)
        logger.info(f"Cleaning up audit logs older than {cutoff_date}")

        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.delete(
                f"{BACKEND_API_URL}/audit-logs/cleanup",
                params={"before": cutoff_date.isoformat()},
                headers={"X-Service": "audit-service"}
            )

            if response.status_code == 200:
                result = response.json()
                deleted_count = result.get("deleted_count", 0)
                logger.info(f"Cleaned up {deleted_count} old audit logs")
                return deleted_count
            else:
                logger.error(f"Error cleaning up audit logs: {response.status_code}")
                return 0

    except Exception as e:
        logger.error(f"Error cleaning up audit logs: {str(e)}", exc_info=True)
        return 0


async def get_audit_logs_for_task(
    task_id: str,
    user_id: str,
    limit: int = 50
) -> list:
    """Get audit logs for a specific task

    Args:
        task_id: Task ID
        user_id: User ID (for authorization)
        limit: Maximum number of logs to return

    Returns:
        List of audit log entries
    """
    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(
                f"{BACKEND_API_URL}/audit-logs/task/{task_id}",
                params={"limit": limit},
                headers={"X-User-ID": user_id}
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting audit logs: {response.status_code}")
                return []

    except Exception as e:
        logger.error(f"Error getting audit logs: {str(e)}", exc_info=True)
        return []


async def get_audit_logs_for_user(
    user_id: str,
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    """Get audit logs for a specific user

    Args:
        user_id: User ID
        limit: Maximum number of logs to return
        offset: Number of logs to skip

    Returns:
        Dictionary with logs and total count
    """
    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(
                f"{BACKEND_API_URL}/audit-logs/user/{user_id}",
                params={"limit": limit, "offset": offset},
                headers={"X-User-ID": user_id}
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting audit logs: {response.status_code}")
                return {"logs": [], "total": 0}

    except Exception as e:
        logger.error(f"Error getting audit logs: {str(e)}", exc_info=True)
        return {"logs": [], "total": 0}
