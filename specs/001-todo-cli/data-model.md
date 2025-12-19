# Data Model: Todo CLI Application

## Entity: Task

### Fields
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Auto-incremented, Primary Key | Unique identifier for each task (FR-002) |
| title | String | Required, 1-200 characters (FR-009) | Task title/description (FR-003) |
| description | String | Optional, max 500 characters (FR-010) | Detailed task description |
| created_date | DateTime | Auto-generated | Timestamp when task was created (FR-015) |
| priority | Enum | Low, Medium, High | Task priority level (FR-003) |
| status | Enum | Pending, In-Progress, Completed (FR-014) | Current status of the task |

### Relationships
- None (standalone entity for Phase I)

### Validation Rules
- Title: 1-200 characters (FR-009)
- Description: Max 500 characters (FR-010)
- Priority: Must be one of Low, Medium, High
- Status: Must be one of Pending, In-Progress, Completed

### State Transitions
- Pending → In-Progress (when user marks as started)
- In-Progress → Completed (when user marks as finished)
- Completed → In-Progress (when user reopens task)
- In-Progress → Pending (when user reverts status)

## Entity: TodoApp (Service Class)

### Methods
| Method | Parameters | Return Type | Description |
|--------|------------|-------------|-------------|
| add_task | title: str, description: str, priority: str | Task | Creates new task with auto-incremented ID (FR-002, FR-003) |
| view_tasks | None | List[Task] | Returns all tasks in formatted table (FR-004) |
| update_task | task_id: int, title: str, description: str | Task | Updates existing task by ID (FR-005) |
| mark_task | task_id: int, status: str | Task | Updates task status by ID (FR-006) |
| delete_task | task_id: int | bool | Removes task by ID (FR-007) |

### Business Logic
- Auto-assign unique IDs to new tasks
- Validate input according to constraints (title length, description length)
- Format task display in table with ID, Title, Description, Status ✓/✗, Created Date, Priority (FR-004)
- Handle edge cases gracefully (invalid IDs, non-existent tasks)
- Return appropriate exit codes (exit code 2 for errors per FR-011)

## Database Schema (SQLModel)
```python
from sqlmodel import SQLModel, Field, create_engine
from datetime import datetime
from enum import Enum

class PriorityEnum(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"

class StatusEnum(str, Enum):
    pending = "Pending"
    in_progress = "In-Progress"
    completed = "Completed"

class Task(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=500)
    created_date: datetime = Field(default_factory=datetime.now)
    priority: PriorityEnum = PriorityEnum.medium
    status: StatusEnum = StatusEnum.pending
```

## Storage Strategy
- Phase I: In-memory SQLite database using SQLModel
- Connection string: `sqlite:///:memory:` for initial implementation
- Phase II: File-based SQLite database for persistence
- Connection string: `sqlite:///todo.db` for persistent implementation