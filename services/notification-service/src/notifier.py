"""Web Push notification sender for notification service"""
import os
import json
import logging
from typing import Dict, Any, Optional
from pywebpush import webpush, WebPushException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# VAPID keys for Web Push (should be loaded from environment)
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY")
VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY")
VAPID_CLAIMS = {
    "sub": os.getenv("VAPID_SUBJECT", "mailto:admin@todoboard.com")
}


async def send_push_notification(
    user_id: str,
    title: str,
    body: str,
    data: Optional[Dict[str, Any]] = None
) -> bool:
    """Send a Web Push notification to a user

    Args:
        user_id: User ID to send notification to
        title: Notification title
        body: Notification body text
        data: Optional additional data to include

    Returns:
        True if notification sent successfully, False otherwise
    """
    try:
        # Get user's push subscription from database
        subscription_info = await get_user_push_subscription(user_id)

        if not subscription_info:
            logger.warning(f"No push subscription found for user {user_id}")
            return False

        # Prepare notification payload
        notification_payload = {
            "title": title,
            "body": body,
            "icon": "/icon-192x192.png",
            "badge": "/badge-72x72.png",
            "data": data or {}
        }

        # Send push notification
        webpush(
            subscription_info=subscription_info,
            data=json.dumps(notification_payload),
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims=VAPID_CLAIMS
        )

        logger.info(f"Successfully sent push notification to user {user_id}")
        return True

    except WebPushException as e:
        logger.error(f"Web Push error for user {user_id}: {str(e)}", exc_info=True)

        # If subscription is invalid (410 Gone), remove it from database
        if e.response and e.response.status_code == 410:
            await remove_user_push_subscription(user_id)
            logger.info(f"Removed invalid push subscription for user {user_id}")

        return False

    except Exception as e:
        logger.error(f"Error sending push notification to user {user_id}: {str(e)}", exc_info=True)
        return False


async def get_user_push_subscription(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user's push subscription from database

    Args:
        user_id: User ID

    Returns:
        Push subscription info or None if not found
    """
    try:
        # TODO: Implement database query to get push subscription
        # For now, return None (subscription management will be implemented later)
        logger.debug(f"Getting push subscription for user {user_id}")
        return None

    except Exception as e:
        logger.error(f"Error getting push subscription for user {user_id}: {str(e)}", exc_info=True)
        return None


async def remove_user_push_subscription(user_id: str) -> bool:
    """Remove user's push subscription from database

    Args:
        user_id: User ID

    Returns:
        True if removed successfully, False otherwise
    """
    try:
        # TODO: Implement database query to remove push subscription
        logger.debug(f"Removing push subscription for user {user_id}")
        return True

    except Exception as e:
        logger.error(f"Error removing push subscription for user {user_id}: {str(e)}", exc_info=True)
        return False


async def save_user_push_subscription(
    user_id: str,
    subscription_info: Dict[str, Any]
) -> bool:
    """Save user's push subscription to database

    Args:
        user_id: User ID
        subscription_info: Push subscription info from browser

    Returns:
        True if saved successfully, False otherwise
    """
    try:
        # TODO: Implement database query to save push subscription
        logger.debug(f"Saving push subscription for user {user_id}")
        return True

    except Exception as e:
        logger.error(f"Error saving push subscription for user {user_id}: {str(e)}", exc_info=True)
        return False
