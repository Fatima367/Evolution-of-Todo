"""MCP tools for task management operations

These tools are exposed to the AI agent via OpenAI Agents SDK,
allowing natural language task management.
"""
import re
import uuid
from datetime import datetime
from typing import Any, Optional

from sqlmodel import Session, select
from agents import function_tool, RunContextWrapper

from src.models.task import Task, TaskStatus, TaskPriority


def _fuzzy_match(query: str, text: str, threshold: float = 0.6) -> float:
    """Simple fuzzy matching using character overlap

    Returns a score between 0 and 1 based on how well query matches text.
    Higher score = better match.
    """
    query = query.lower().strip()
    text = text.lower().strip()

    if not query or not text:
        return 0.0

    # Exact match
    if query == text:
        return 1.0

    # Check if query is contained in text
    if query in text:
        return 0.9

    # Check if text is contained in query
    if text in query:
        return 0.8

    # Word-level matching
    query_words = set(query.split())
    text_words = set(text.split())

    if query_words and text_words:
        # Jaccard similarity for words
        intersection = len(query_words & text_words)
        union = len(query_words | text_words)
        word_score = intersection / union if union > 0 else 0

        # Character n-gram similarity (bigrams)
        query_bigrams = set(zip(query, query[1:])) if len(query) > 1 else {query}
        text_bigrams = set(zip(text, text[1:])) if len(text) > 1 else {text}

        if query_bigrams and text_bigrams:
            bigram_intersection = len(query_bigrams & text_bigrams)
            bigram_union = len(query_bigrams | text_bigrams)
            bigram_score = bigram_intersection / bigram_union if bigram_union > 0 else 0
        else:
            bigram_score = 0

        # Combined score with weight on word matching
        combined = (0.4 * word_score + 0.6 * bigram_score)
        return combined if combined >= threshold else 0.0

    return 0.0


def _extract_task_name_pattern(message: str) -> Optional[str]:
    """Extract task name from patterns like 'the X task' or 'my X task'

    Args:
        message: User's message

    Returns:
        Extracted task name or None
    """
    patterns = [
        r"the\s+(.+?)\s+task\b",
        r"my\s+(.+?)\s+task\b",
        r"that\s+(.+?)\s+task\b",
        r"task\s+(?:called|named)?\s*['\"]?(.+?)['\"]?",
    ]

    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            name = match.group(1).strip().strip("'\"")
            if name and len(name) > 1:
                return name

    return None


class TaskToolContext:
    """Context passed to tools containing session, user_id and thread info

    This context is passed via RunContextWrapper when running the agent.
    """
    session: Session
    user_id: str  # UUID as string
    thread_id: str

    def __init__(self, session: Session, user_id: str, thread_id: str = ""):
        self.session = session
        self.user_id = user_id
        self.thread_id = thread_id


def create_task_tools(session: Session, user_id: str, thread_id: str = "") -> list[Any]:
    """Create MCP tools for task management

    Args:
        session: Database session
        user_id: User ID for data isolation
        thread_id: Current conversation/thread ID

    Returns:
        List of decorated function tools
    """
    context = TaskToolContext(session=session, user_id=user_id, thread_id=thread_id)

    @function_tool(name_override="add_task")
    def add_task(ctx: RunContextWrapper[TaskToolContext], title: str, description: str | None = None, priority: str = "medium") -> dict[str, str]:
        """Create a new task with a title and optional description and priority"""
        session = ctx.context.session
        user_id = ctx.context.user_id

        try:
            priority_enum = TaskPriority(priority.lower())
        except ValueError:
            priority_enum = TaskPriority.MEDIUM

        task = Task(
            title=title,
            description=description,
            priority=priority_enum,
            user_id=uuid.UUID(user_id),
            status=TaskStatus.PENDING
        )

        session.add(task)
        session.commit()
        session.refresh(task)

        return {
            "task_id": str(task.id),
            "status": "created",
            "title": task.title,
            "priority": task.priority.value
        }

    @function_tool(name_override="list_tasks")
    def list_tasks(ctx: RunContextWrapper[TaskToolContext], status: str | None = None, limit: int = 20) -> dict[str, str | list[dict[str, str]]]:
        """List all tasks, optionally filtered by status (pending, in_progress, completed, or omit for all)"""
        session = ctx.context.session
        user_id = ctx.context.user_id

        statement = select(Task).where(Task.user_id == uuid.UUID(user_id))

        if status and status.lower() != "all":
            try:
                status_enum = TaskStatus(status.lower())
                statement = statement.where(Task.status == status_enum)
            except ValueError:
                pass

        statement = statement.order_by(Task.created_at.desc()).limit(limit)
        tasks = session.exec(statement).all()

        task_list = []
        for task in tasks:
            task_data = {
                "id": str(task.id),
                "title": task.title,
                "description": task.description or "",
                "status": task.status.value,
                "priority": task.priority.value,
                "due_date": str(task.due_date) if task.due_date else "",
                "created_at": str(task.created_at)
            }
            task_list.append(task_data)

        return {
            "tasks": task_list,
            "count": len(task_list),
            "message": f"Found {len(task_list)} task(s)" if task_list else "No tasks found."
        }

    @function_tool(name_override="complete_task")
    def complete_task(ctx: RunContextWrapper[TaskToolContext], task_id: str) -> dict[str, str]:
        """Mark a task as completed using its ID"""
        session = ctx.context.session
        user_id = ctx.context.user_id

        try:
            task_uuid = uuid.UUID(task_id)
        except ValueError:
            return {"error": f"Invalid task ID format: {task_id}", "status": "error"}

        statement = select(Task).where(
            Task.id == task_uuid,
            Task.user_id == uuid.UUID(user_id)
        )
        task = session.exec(statement).first()

        if not task:
            return {"error": f"Task not found with ID: {task_id}", "status": "error"}

        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()

        session.add(task)
        session.commit()

        return {
            "task_id": str(task.id),
            "status": "completed",
            "title": task.title
        }

    @function_tool(name_override="delete_task")
    def delete_task(ctx: RunContextWrapper[TaskToolContext], task_id: str) -> dict[str, str]:
        """Delete a task using its ID"""
        session = ctx.context.session
        user_id = ctx.context.user_id

        try:
            task_uuid = uuid.UUID(task_id)
        except ValueError:
            return {"error": f"Invalid task ID format: {task_id}", "status": "error"}

        statement = select(Task).where(
            Task.id == task_uuid,
            Task.user_id == uuid.UUID(user_id)
        )
        task = session.exec(statement).first()

        if not task:
            return {"error": f"Task not found with ID: {task_id}", "status": "error"}

        title = task.title
        session.delete(task)
        session.commit()

        return {
            "task_id": task_id,
            "status": "deleted",
            "title": title
        }

    @function_tool(name_override="update_task")
    def update_task(ctx: RunContextWrapper[TaskToolContext], task_id: str, title: str | None = None, description: str | None = None, priority: str | None = None, status: str | None = None) -> dict[str, str]:
        """Update a task's title, description, priority, or status"""
        session = ctx.context.session
        user_id = ctx.context.user_id

        try:
            task_uuid = uuid.UUID(task_id)
        except ValueError:
            return {"error": f"Invalid task ID format: {task_id}", "status": "error"}

        statement = select(Task).where(
            Task.id == task_uuid,
            Task.user_id == uuid.UUID(user_id)
        )
        task = session.exec(statement).first()

        if not task:
            return {"error": f"Task not found with ID: {task_id}", "status": "error"}

        updated = []
        if title is not None:
            task.title = title
            updated.append("title")
        if description is not None:
            task.description = description
            updated.append("description")
        if priority is not None:
            try:
                task.priority = TaskPriority(priority.lower())
                updated.append("priority")
            except ValueError:
                pass
        if status is not None:
            try:
                new_status = TaskStatus(status.lower())
                task.status = new_status
                updated.append("status")
                if new_status == TaskStatus.COMPLETED:
                    task.completed_at = datetime.utcnow()
                else:
                    task.completed_at = None
            except ValueError:
                pass

        if not updated:
            return {"status": "no_change", "message": "No fields to update", "title": task.title}

        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()

        return {
            "status": "updated",
            "title": task.title,
            "priority": task.priority.value,
            "task_status": task.status.value,
            "changes": ", ".join(updated)
        }

    @function_tool(name_override="find_task_by_name")
    def find_task_by_name(ctx: RunContextWrapper[TaskToolContext], task_name: str) -> dict[str, str | list[dict[str, str]]]:
        """Find tasks matching a name with fuzzy matching. Returns matching tasks or asks for clarification if ambiguous.

        Args:
            task_name: Partial or full task name to search for

        Returns:
            dict with matches list, count, and disambiguation guidance
        """
        session = ctx.context.session
        user_id = ctx.context.user_id

        # Get all user's tasks
        statement = select(Task).where(Task.user_id == uuid.UUID(user_id))
        tasks = session.exec(statement).all()

        if not tasks:
            return {
                "status": "not_found",
                "message": "You don't have any tasks yet.",
                "matches": [],
                "count": 0
            }

        # Score each task
        scored = []
        for task in tasks:
            score = _fuzzy_match(task_name, task.title)
            if score > 0:
                scored.append((score, task))

        # Sort by score descending
        scored.sort(key=lambda x: -x[0])

        if not scored:
            return {
                "status": "not_found",
                "message": f"No tasks matching '{task_name}' found.",
                "matches": [],
                "count": 0,
                "suggestion": "Try using a more specific name or say 'list tasks' to see all your tasks."
            }

        # Get top matches (score >= 0.6)
        threshold = 0.6
        top_matches = [(s, t) for s, t in scored if s >= threshold]

        if len(top_matches) == 1:
            # Single match - return it
            score, task = top_matches[0]
            return {
                "status": "found",
                "task_id": str(task.id),
                "title": task.title,
                "score": float(score),
                "matches": [{
                    "id": str(task.id),
                    "title": task.title,
                    "status": task.status.value,
                    "priority": task.priority.value
                }],
                "count": 1,
                "message": f"Found 1 matching task: {task.title}"
            }

        if len(top_matches) > 1:
            # Multiple matches - return all for disambiguation
            matches_data = [
                {
                    "id": str(t.id),
                    "title": t.title,
                    "status": t.status.value,
                    "priority": t.priority.value
                }
                for _, t in top_matches
            ]
            return {
                "status": "ambiguous",
                "message": f"Found {len(top_matches)} tasks matching '{task_name}'. Please specify which one.",
                "matches": matches_data,
                "count": len(top_matches),
                "disambiguation_required": True,
                "suggestion": "Tell me the task ID or be more specific about which task you mean."
            }

        # No strong matches but some weak matches exist
        weak_matches = scored[:3]  # Top 3 weak matches
        matches_data = [
            {
                "id": str(t.id),
                "title": t.title,
                "status": t.status.value,
                "priority": t.priority.value,
                "score": float(s)
            }
            for s, t in weak_matches
        ]
        return {
            "status": "partial_match",
            "message": f"Found {len(weak_matches)} tasks that might be related.",
            "matches": matches_data,
            "count": len(weak_matches),
            "disambiguation_required": True,
            "suggestion": "Did you mean one of these tasks?"
        }

    @function_tool(name_override="bulk_complete_tasks")
    def bulk_complete_tasks(ctx: RunContextWrapper[TaskToolContext], status: str = "pending") -> dict[str, str | int]:
        """Complete all tasks with the specified status (default: pending)

        Args:
            status: Task status to filter by (pending, in_progress). Defaults to pending.

        Returns:
            dict with count of completed tasks
        """
        session = ctx.context.session
        user_id = ctx.context.user_id

        try:
            status_enum = TaskStatus(status.lower())
        except ValueError:
            # Default to pending if invalid status
            status_enum = TaskStatus.PENDING

        statement = select(Task).where(
            Task.user_id == uuid.UUID(user_id),
            Task.status == status_enum
        )
        tasks = session.exec(statement).all()

        if not tasks:
            return {
                "status": "no_tasks",
                "message": f"No {status} tasks found to complete.",
                "count": 0
            }

        completed_count = 0
        for task in tasks:
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.updated_at = datetime.utcnow()
            session.add(task)
            completed_count += 1

        session.commit()

        return {
            "status": "completed",
            "message": f"Completed {completed_count} task(s).",
            "count": completed_count,
            "filter_status": status
        }

    @function_tool(name_override="bulk_delete_completed")
    def bulk_delete_completed(ctx: RunContextWrapper[TaskToolContext]) -> dict[str, str | int]:
        """Delete all completed tasks

        Returns:
            dict with count of deleted tasks
        """
        session = ctx.context.session
        user_id = ctx.context.user_id

        statement = select(Task).where(
            Task.user_id == uuid.UUID(user_id),
            Task.status == TaskStatus.COMPLETED
        )
        tasks = session.exec(statement).all()

        if not tasks:
            return {
                "status": "no_tasks",
                "message": "No completed tasks to delete.",
                "count": 0
            }

        deleted_count = 0
        for task in tasks:
            session.delete(task)
            deleted_count += 1

        session.commit()

        return {
            "status": "deleted",
            "message": f"Deleted {deleted_count} completed task(s).",
            "count": deleted_count
        }

    @function_tool(name_override="clear_all_tasks")
    def clear_all_tasks(ctx: RunContextWrapper[TaskToolContext], confirmation: str) -> dict[str, str | int]:
        """Delete ALL tasks (requires explicit confirmation phrase)

        Args:
            confirmation: Must be "confirm" or "yes" to proceed

        Returns:
            dict with count of deleted tasks
        """
        if confirmation.lower() not in ["confirm", "yes", "delete all"]:
            return {
                "status": "cancelled",
                "message": "Task deletion cancelled. To delete all tasks, say 'delete all my tasks'.",
                "count": 0
            }

        session = ctx.context.session
        user_id = ctx.context.user_id

        statement = select(Task).where(Task.user_id == uuid.UUID(user_id))
        tasks = session.exec(statement).all()

        if not tasks:
            return {
                "status": "no_tasks",
                "message": "No tasks to delete.",
                "count": 0
            }

        deleted_count = 0
        for task in tasks:
            session.delete(task)
            deleted_count += 1

        session.commit()

        return {
            "status": "deleted",
            "message": f"Deleted all {deleted_count} task(s).",
            "count": deleted_count
        }

    return [
        add_task, list_tasks, complete_task, delete_task, update_task,
        find_task_by_name, bulk_complete_tasks, bulk_delete_completed, clear_all_tasks
    ]
