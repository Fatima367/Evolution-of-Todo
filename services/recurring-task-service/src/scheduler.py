"""Recurring task scheduler logic for creating next occurrences"""
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from uuid import UUID
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Backend API configuration
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://backend:8000")
API_TIMEOUT = 30.0


async def create_next_occurrence(
    task_id: str,
    user_id: str,
    task_data: Dict[str, Any]
) -> bool:
    """Create the next occurrence of a recurring task

    Args:
        task_id: Original task ID
        user_id: User ID
        task_data: Task data from the completed task

    Returns:
        True if next occurrence created successfully, False otherwise
    """
    try:
        logger.info(f"Creating next occurrence for recurring task {task_id}")

        # Get recurring pattern from backend API
        recurring_pattern = await get_recurring_pattern(task_id, user_id)

        if not recurring_pattern:
            logger.warning(f"No recurring pattern found for task {task_id}")
            return False

        # Calculate next occurrence date
        next_due_date = calculate_next_occurrence(recurring_pattern)

        if not next_due_date:
            logger.info(f"Recurring pattern has ended for task {task_id}")
            return True  # Pattern ended naturally, not an error

        # Create new task with updated due date
        new_task_data = {
            "title": task_data.get("title"),
            "description": task_data.get("description"),
            "priority": task_data.get("priority"),
            "due_date": next_due_date.isoformat(),
            "tags": task_data.get("tags"),
            "is_favorite": task_data.get("is_favorite", False),
            "recurring_type": task_data.get("recurring_type"),
            "reminder_offset": task_data.get("reminder_offset", 15)
        }

        # Create task via backend API
        success = await create_task_via_api(user_id, new_task_data)

        if success:
            # Update last_generated_at in recurring pattern
            await update_recurring_pattern_timestamp(
                recurring_pattern["id"],
                user_id,
                next_due_date
            )
            logger.info(f"Successfully created next occurrence for task {task_id}")
            return True
        else:
            logger.error(f"Failed to create next occurrence for task {task_id}")
            return False

    except Exception as e:
        logger.error(f"Error creating next occurrence for task {task_id}: {str(e)}", exc_info=True)
        return False


def calculate_next_occurrence(recurring_pattern: Dict[str, Any]) -> Optional[datetime]:
    """Calculate the next occurrence date based on recurring pattern

    Args:
        recurring_pattern: Recurring pattern data

    Returns:
        Next occurrence datetime or None if pattern has ended
    """
    try:
        frequency = recurring_pattern.get("frequency")
        interval = recurring_pattern.get("interval", 1)
        end_date_str = recurring_pattern.get("end_date")
        last_generated_str = recurring_pattern.get("last_generated_at")

        # Start from last generated date or now
        if last_generated_str:
            base_date = datetime.fromisoformat(last_generated_str.replace('Z', '+00:00'))
        else:
            base_date = datetime.utcnow()

        # Calculate next date based on frequency
        if frequency == "daily":
            next_date = base_date + timedelta(days=interval)

        elif frequency == "weekly":
            day_of_week = recurring_pattern.get("day_of_week", 0)
            days_ahead = (day_of_week - base_date.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7 * interval
            next_date = base_date + timedelta(days=days_ahead)

        elif frequency == "monthly":
            day_of_month = recurring_pattern.get("day_of_month", 1)
            month = base_date.month + interval
            year = base_date.year
            while month > 12:
                month -= 12
                year += 1

            # Handle day overflow (e.g., Feb 31 -> Feb 28/29)
            import calendar
            max_day = calendar.monthrange(year, month)[1]
            day = min(day_of_month, max_day)

            next_date = base_date.replace(year=year, month=month, day=day)

        elif frequency == "yearly":
            day_of_month = recurring_pattern.get("day_of_month", 1)
            month_of_year = recurring_pattern.get("month_of_year", 1)
            year = base_date.year + interval

            # Handle leap year edge case
            import calendar
            max_day = calendar.monthrange(year, month_of_year)[1]
            day = min(day_of_month, max_day)

            next_date = base_date.replace(year=year, month=month_of_year, day=day)

        else:
            logger.warning(f"Unknown frequency: {frequency}")
            return None

        # Check if next date exceeds end_date
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
            if next_date >= end_date:
                logger.info(f"Next occurrence {next_date} exceeds end date {end_date}")
                return None

        return next_date

    except Exception as e:
        logger.error(f"Error calculating next occurrence: {str(e)}", exc_info=True)
        return None


async def get_recurring_pattern(task_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    """Get recurring pattern from backend API

    Args:
        task_id: Task ID
        user_id: User ID

    Returns:
        Recurring pattern data or None if not found
    """
    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(
                f"{BACKEND_API_URL}/recurring/task/{task_id}",
                headers={"X-User-ID": user_id}  # Simplified auth for microservice
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                logger.error(f"Error getting recurring pattern: {response.status_code}")
                return None

    except Exception as e:
        logger.error(f"Error calling backend API: {str(e)}", exc_info=True)
        return None


async def create_task_via_api(user_id: str, task_data: Dict[str, Any]) -> bool:
    """Create a new task via backend API

    Args:
        user_id: User ID
        task_data: Task creation data

    Returns:
        True if created successfully, False otherwise
    """
    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.post(
                f"{BACKEND_API_URL}/tasks",
                json=task_data,
                headers={"X-User-ID": user_id}  # Simplified auth for microservice
            )

            if response.status_code == 201:
                logger.info(f"Created new task via API")
                return True
            else:
                logger.error(f"Error creating task: {response.status_code} - {response.text}")
                return False

    except Exception as e:
        logger.error(f"Error calling backend API: {str(e)}", exc_info=True)
        return False


async def update_recurring_pattern_timestamp(
    pattern_id: int,
    user_id: str,
    last_generated_at: datetime
) -> bool:
    """Update last_generated_at timestamp in recurring pattern

    Args:
        pattern_id: Pattern ID
        user_id: User ID
        last_generated_at: Timestamp of last generated occurrence

    Returns:
        True if updated successfully, False otherwise
    """
    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.put(
                f"{BACKEND_API_URL}/recurring/{pattern_id}",
                json={"last_generated_at": last_generated_at.isoformat()},
                headers={"X-User-ID": user_id}  # Simplified auth for microservice
            )

            if response.status_code == 200:
                return True
            else:
                logger.error(f"Error updating recurring pattern: {response.status_code}")
                return False

    except Exception as e:
        logger.error(f"Error calling backend API: {str(e)}", exc_info=True)
        return False
