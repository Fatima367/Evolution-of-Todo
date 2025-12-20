"""CLI entry point with menu-driven interface for Todo application."""

import sys
from typing import NoReturn

import inquirer
from rich.console import Console
from rich.panel import Panel

from src.services import TodoApp
from src.lib.utils import (
    format_task_table,
    validate_title,
    validate_description,
    validate_priority,
    validate_status,
    display_error,
    display_success,
    display_info,
)


console = Console()


def display_menu() -> str:
    """
    Display main menu and get user selection.

    Returns:
        str: User's menu selection
    """
    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]📝 Todo CLI Application[/bold cyan]\n"
        "[dim]Manage your tasks with style![/dim]",
        border_style="cyan"
    ))

    questions = [
        inquirer.List(
            "action",
            message="What would you like to do?",
            choices=[
                ("📋 View Tasks", "view"),
                ("➕ Add Task", "add"),
                ("✏️  Update Task", "update"),
                ("✓  Mark Task Status", "mark"),
                ("🗑️  Delete Task", "delete"),
                ("❌ Exit", "exit"),
            ],
        ),
    ]

    answers = inquirer.prompt(questions)
    return answers["action"] if answers else "exit"


def handle_view_tasks(app: TodoApp) -> None:
    """Display all tasks in a formatted table."""
    tasks = app.view_tasks()

    if not tasks:
        display_info("No tasks found. Add your first task!")
        return

    table = format_task_table(tasks)
    console.print("\n")
    console.print(table)
    console.print("\n")


def handle_add_task(app: TodoApp) -> None:
    """Prompt user to add a new task."""
    console.print("\n[bold cyan]Add New Task[/bold cyan]\n")

    questions = [
        inquirer.Text("title", message="Enter task title (1-200 characters)"),
        inquirer.Text("description", message="Enter task description (optional, max 500 chars)", default=""),
        inquirer.List(
            "priority",
            message="Select priority level",
            choices=["Low", "Medium", "High"],
            default="Medium",
        ),
    ]

    answers = inquirer.prompt(questions)
    if not answers:
        display_info("Task creation cancelled.")
        return

    title = answers["title"]
    description = answers["description"]
    priority = answers["priority"]

    # Validate inputs
    if not validate_title(title):
        display_error("Invalid title. Must be 1-200 characters.")
        sys.exit(2)

    if not validate_description(description):
        display_error("Invalid description. Must be max 500 characters.")
        sys.exit(2)

    try:
        task = app.add_task(title=title, description=description, priority=priority)
        display_success(f"Task created successfully! ID: {task.id}")
    except Exception as e:
        display_error(f"Failed to create task: {str(e)}")
        sys.exit(2)


def handle_update_task(app: TodoApp) -> None:
    """Prompt user to update an existing task."""
    console.print("\n[bold cyan]Update Task[/bold cyan]\n")

    # First show tasks
    handle_view_tasks(app)

    questions = [
        inquirer.Text("task_id", message="Enter task ID to update"),
        inquirer.Text("title", message="Enter new title (leave blank to keep current)"),
        inquirer.Text("description", message="Enter new description (leave blank to keep current)"),
    ]

    answers = inquirer.prompt(questions)
    if not answers:
        display_info("Update cancelled.")
        return

    try:
        task_id = int(answers["task_id"])
    except ValueError:
        display_error("Invalid task ID. Must be a number.")
        sys.exit(2)

    title = answers["title"] if answers["title"] else None
    description = answers["description"] if answers["description"] else None

    # Validate inputs if provided
    if title and not validate_title(title):
        display_error("Invalid title. Must be 1-200 characters.")
        sys.exit(2)

    if description and not validate_description(description):
        display_error("Invalid description. Must be max 500 characters.")
        sys.exit(2)

    task = app.update_task(task_id=task_id, title=title, description=description)

    if task:
        display_success(f"Task {task_id} updated successfully!")
    else:
        display_error(f"Task with ID {task_id} not found.")
        sys.exit(2)


def handle_mark_task(app: TodoApp) -> None:
    """Prompt user to mark task status."""
    console.print("\n[bold cyan]Mark Task Status[/bold cyan]\n")

    # First show tasks
    handle_view_tasks(app)

    questions = [
        inquirer.Text("task_id", message="Enter task ID to update status"),
        inquirer.List(
            "status",
            message="Select new status",
            choices=["Pending", "In-Progress", "Completed"],
        ),
    ]

    answers = inquirer.prompt(questions)
    if not answers:
        display_info("Status update cancelled.")
        return

    try:
        task_id = int(answers["task_id"])
    except ValueError:
        display_error("Invalid task ID. Must be a number.")
        sys.exit(2)

    status = answers["status"]

    try:
        task = app.mark_task(task_id=task_id, status=status)

        if task:
            display_success(f"Task {task_id} marked as {status}!")
        else:
            display_error(f"Task with ID {task_id} not found.")
            sys.exit(2)
    except ValueError as e:
        display_error(str(e))
        sys.exit(2)


def handle_delete_task(app: TodoApp) -> None:
    """Prompt user to delete a task."""
    console.print("\n[bold cyan]Delete Task[/bold cyan]\n")

    # First show tasks
    handle_view_tasks(app)

    questions = [
        inquirer.Text("task_id", message="Enter task ID to delete"),
        inquirer.Confirm("confirm", message="Are you sure you want to delete this task?", default=False),
    ]

    answers = inquirer.prompt(questions)
    if not answers or not answers["confirm"]:
        display_info("Deletion cancelled.")
        return

    try:
        task_id = int(answers["task_id"])
    except ValueError:
        display_error("Invalid task ID. Must be a number.")
        sys.exit(2)

    success = app.delete_task(task_id=task_id)

    if success:
        display_success(f"Task {task_id} deleted successfully!")
    else:
        display_error(f"Task with ID {task_id} not found.")
        sys.exit(2)


def main() -> NoReturn:
    """Main application entry point."""
    try:
        app = TodoApp()

        console.print("[bold green]Welcome to Todo CLI![/bold green]")

        while True:
            try:
                action = display_menu()

                if action == "exit":
                    console.print("\n[bold cyan]Goodbye! 👋[/bold cyan]\n")
                    sys.exit(0)
                elif action == "view":
                    handle_view_tasks(app)
                elif action == "add":
                    handle_add_task(app)
                elif action == "update":
                    handle_update_task(app)
                elif action == "mark":
                    handle_mark_task(app)
                elif action == "delete":
                    handle_delete_task(app)
                else:
                    display_error("Invalid action selected.")

            except KeyboardInterrupt:
                console.print("\n\n[bold cyan]Goodbye! 👋[/bold cyan]\n")
                sys.exit(0)
            except Exception as e:
                display_error(f"An unexpected error occurred: {str(e)}")
                console.print("[dim]Press Ctrl+C to exit[/dim]")

    except KeyboardInterrupt:
        console.print("\n\n[bold cyan]Goodbye! 👋[/bold cyan]\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
