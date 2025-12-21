"""Utility functions for input validation, formatting, and display."""

import logging
from datetime import datetime
from typing import List

from rich.console import Console
from rich.table import Table

from src.models import Task, PriorityEnum, StatusEnum


console = Console()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('todo_app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def validate_title(title: str) -> bool:
    """
    Validate task title length.

    Args:
        title: Task title string

    Returns:
        bool: True if valid (1-200 characters), False otherwise
    """
    return 1 <= len(title) <= 200


def validate_description(description: str) -> bool:
    """
    Validate task description length.

    Args:
        description: Task description string

    Returns:
        bool: True if valid (max 500 characters), False otherwise
    """
    return len(description) <= 500


def validate_priority(priority: str) -> bool:
    """
    Validate task priority value.

    Args:
        priority: Priority string (case-insensitive)

    Returns:
        bool: True if valid (Low, Medium, High), False otherwise
    """
    try:
        priority_upper = priority.upper()
        return priority_upper in ["LOW", "MEDIUM", "HIGH"]
    except (AttributeError, TypeError):
        return False


def validate_status(status: str) -> bool:
    """
    Validate task status value.

    Args:
        status: Status string (case-insensitive)

    Returns:
        bool: True if valid (Pending, In-Progress, Completed), False otherwise
    """
    try:
        # Normalize status for comparison
        status_normalized = status.replace(" ", "-").replace("_", "-").upper()
        valid_statuses = ["PENDING", "IN-PROGRESS", "COMPLETED"]
        return status_normalized in valid_statuses
    except (AttributeError, TypeError):
        return False


def get_priority_color(priority: PriorityEnum) -> str:
    """
    Get color code for priority level.

    Args:
        priority: Priority enum value

    Returns:
        str: Rich color code
    """
    color_map = {
        PriorityEnum.LOW: "green",
        PriorityEnum.MEDIUM: "yellow",
        PriorityEnum.HIGH: "red",
    }
    return color_map.get(priority, "white")


def get_status_symbol(status: StatusEnum) -> str:
    """
    Get symbol for task status.

    Args:
        status: Status enum value

    Returns:
        str: Status symbol (✓ for completed, ✗ for others)
    """
    return "✓" if status == StatusEnum.COMPLETED else "✗"


def format_task_table(tasks: List[Task]) -> Table:
    """
    Format tasks into a rich table for display.

    Args:
        tasks: List of Task objects

    Returns:
        Table: Rich table with formatted task data
    """
    table = Table(title="📋 Your Tasks", show_header=True, header_style="bold magenta")

    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Title", style="white")
    table.add_column("Description", style="dim")
    table.add_column("Status", justify="center")
    table.add_column("Created", style="blue")
    table.add_column("Priority", justify="center")

    for task in tasks:
        priority_color = get_priority_color(task.priority)
        status_symbol = get_status_symbol(task.status)

        # Format created date
        created_str = task.created_date.strftime("%Y-%m-%d %H:%M")

        # Truncate description if too long
        description_display = task.description[:50] + "..." if len(task.description) > 50 else task.description

        table.add_row(
            str(task.id),
            task.title,
            description_display,
            f"[{'green' if task.status == StatusEnum.COMPLETED else 'red'}]{status_symbol}[/]",
            created_str,
            f"[{priority_color}]{task.priority.value}[/]",
        )

    return table


def display_error(message: str) -> None:
    """
    Display error message with formatting.

    Args:
        message: Error message to display
    """
    console.print(f"[bold red]Error:[/bold red] {message}")


def display_success(message: str) -> None:
    """
    Display success message with formatting.

    Args:
        message: Success message to display
    """
    console.print(f"[bold green]Success:[/bold green] {message}")


def display_info(message: str) -> None:
    """
    Display info message with formatting.

    Args:
        message: Info message to display
    """
    console.print(f"[bold blue]Info:[/bold blue] {message}")
