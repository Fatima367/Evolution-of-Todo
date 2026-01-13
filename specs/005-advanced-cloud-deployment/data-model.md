# Data Model: Advanced Cloud Deployment

**Feature**: 005-advanced-cloud-deployment
**Date**: 2026-01-12
**Phase**: Phase 1 - Design & Contracts

## Overview

This document defines the database schema extensions and entity relationships for Phase V advanced features. All changes maintain backward compatibility with existing Phase II/III schema.

---

## Database: Neon Serverless PostgreSQL

**Connection**: Existing Neon database from Phase II
**ORM**: SQLModel (Pydantic + SQLAlchemy)
**Migrations**: Alembic

---

## Schema Changes

### Extended Table: `tasks`

**Purpose**: Extend existing tasks table with advanced features (priorities, tags, due dates)

**New Columns**:
```sql
ALTER TABLE tasks ADD COLUMN priority VARCHAR(10) DEFAULT 'medium';
ALTER TABLE tasks ADD COLUMN tags TEXT[]; -- PostgreSQL array
ALTER TABLE tasks ADD COLUMN due_date TIMESTAMP WITH TIME ZONE;
ALTER TABLE tasks ADD COLUMN reminder_offset INTEGER DEFAULT 15; -- minutes before due_date
ALTER TABLE tasks ADD COLUMN search_vector TSVECTOR; -- Full-text search

-- Indexes for performance
CREATE INDEX idx_tasks_user_priority ON tasks(user_id, priority);
CREATE INDEX idx_tasks_user_due_date ON tasks(user_id, due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_tasks_tags ON tasks USING GIN(tags);
CREATE INDEX idx_tasks_search ON tasks USING GIN(search_vector);
```

**Complete Schema** (existing + new columns):
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique task identifier |
| user_id | VARCHAR(255) | NOT NULL, FOREIGN KEY → users.id | Owner of the task |
| title | VARCHAR(255) | NOT NULL | Task title |
| description | TEXT | NULLABLE | Task description |
| completed | BOOLEAN | DEFAULT FALSE | Completion status |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update timestamp |
| **priority** | **VARCHAR(10)** | **DEFAULT 'medium'** | **Priority level: high, medium, low** |
| **tags** | **TEXT[]** | **DEFAULT '{}'** | **Array of tag strings** |
| **due_date** | **TIMESTAMP WITH TIME ZONE** | **NULLABLE** | **When task is due (UTC)** |
| **reminder_offset** | **INTEGER** | **DEFAULT 15** | **Minutes before due_date to send reminder** |
| **search_vector** | **TSVECTOR** | **GENERATED** | **Full-text search index** |

**Validation Rules**:
- `priority` must be one of: 'high', 'medium', 'low'
- `tags` array max 10 tags, each tag max 50 characters
- `due_date` must be in future (or null)
- `reminder_offset` must be between 0 and 1440 (24 hours)

**SQLModel Definition**:
```python
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import ARRAY, String, func
from datetime import datetime
from typing import Optional, List

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=255)
    description: Optional[str] = None
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Phase V additions
    priority: str = Field(default="medium", max_length=10)
    tags: List[str] = Field(default=[], sa_column=Column(ARRAY(String)))
    due_date: Optional[datetime] = None
    reminder_offset: int = Field(default=15)  # minutes
```

---

### New Table: `recurring_patterns`

**Purpose**: Store recurrence configuration for recurring tasks

**Schema**:
```sql
CREATE TABLE recurring_patterns (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL UNIQUE REFERENCES tasks(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    frequency VARCHAR(20) NOT NULL, -- 'daily', 'weekly', 'monthly', 'yearly', 'custom'
    interval INTEGER NOT NULL DEFAULT 1, -- every N days/weeks/months/years
    day_of_week INTEGER, -- 0-6 for weekly (0=Monday)
    day_of_month INTEGER, -- 1-31 for monthly
    month_of_year INTEGER, -- 1-12 for yearly
    end_date TIMESTAMP WITH TIME ZONE, -- when to stop recurring (null = forever)
    last_generated_at TIMESTAMP WITH TIME ZONE, -- last time next occurrence was created
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_recurring_user ON recurring_patterns(user_id);
CREATE INDEX idx_recurring_task ON recurring_patterns(task_id);
```

**Columns**:
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique pattern identifier |
| task_id | INTEGER | UNIQUE, FOREIGN KEY → tasks.id | Associated task (1:1 relationship) |
| user_id | VARCHAR(255) | FOREIGN KEY → users.id | Owner (for isolation) |
| frequency | VARCHAR(20) | NOT NULL | Recurrence frequency |
| interval | INTEGER | DEFAULT 1 | Repeat every N periods |
| day_of_week | INTEGER | NULLABLE | For weekly: 0-6 (0=Monday) |
| day_of_month | INTEGER | NULLABLE | For monthly: 1-31 |
| month_of_year | INTEGER | NULLABLE | For yearly: 1-12 |
| end_date | TIMESTAMP | NULLABLE | Stop recurring after this date |
| last_generated_at | TIMESTAMP | NULLABLE | Last occurrence creation time |
| created_at | TIMESTAMP | DEFAULT NOW() | Pattern creation time |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update time |

**Validation Rules**:
- `frequency` must be one of: 'daily', 'weekly', 'monthly', 'yearly', 'custom'
- `interval` must be >= 1
- `day_of_week` required if frequency='weekly', must be 0-6
- `day_of_month` required if frequency='monthly', must be 1-31
- `month_of_year` required if frequency='yearly', must be 1-12
- `end_date` must be after task.due_date (if set)

**SQLModel Definition**:
```python
class RecurringPattern(SQLModel, table=True):
    __tablename__ = "recurring_patterns"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id", unique=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    frequency: str = Field(max_length=20)  # daily, weekly, monthly, yearly, custom
    interval: int = Field(default=1, ge=1)
    day_of_week: Optional[int] = Field(default=None, ge=0, le=6)
    day_of_month: Optional[int] = Field(default=None, ge=1, le=31)
    month_of_year: Optional[int] = Field(default=None, ge=1, le=12)
    end_date: Optional[datetime] = None
    last_generated_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

---

### New Table: `reminders`

**Purpose**: Track scheduled reminders for tasks with due dates

**Schema**:
```sql
CREATE TABLE reminders (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    remind_at TIMESTAMP WITH TIME ZONE NOT NULL, -- when to send reminder
    sent BOOLEAN DEFAULT FALSE, -- has reminder been sent
    sent_at TIMESTAMP WITH TIME ZONE, -- when reminder was sent
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_reminders_user ON reminders(user_id);
CREATE INDEX idx_reminders_task ON reminders(task_id);
CREATE INDEX idx_reminders_pending ON reminders(remind_at, sent) WHERE sent = FALSE;
```

**Columns**:
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique reminder identifier |
| task_id | INTEGER | FOREIGN KEY → tasks.id | Associated task |
| user_id | VARCHAR(255) | FOREIGN KEY → users.id | Owner (for isolation) |
| remind_at | TIMESTAMP | NOT NULL | When to send reminder (UTC) |
| sent | BOOLEAN | DEFAULT FALSE | Has reminder been sent |
| sent_at | TIMESTAMP | NULLABLE | When reminder was sent |
| created_at | TIMESTAMP | DEFAULT NOW() | Reminder creation time |

**Validation Rules**:
- `remind_at` must be in future when created
- `remind_at` must be before task.due_date
- `sent_at` must be set when sent=TRUE

**SQLModel Definition**:
```python
class Reminder(SQLModel, table=True):
    __tablename__ = "reminders"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id", index=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    remind_at: datetime = Field(index=True)
    sent: bool = Field(default=False, index=True)
    sent_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

### New Table: `audit_logs`

**Purpose**: Complete audit trail of all task operations for compliance and debugging

**Schema**:
```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    task_id INTEGER, -- nullable (task may be deleted)
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    operation VARCHAR(20) NOT NULL, -- 'created', 'updated', 'completed', 'deleted'
    changes JSONB, -- what changed (before/after values)
    request_id VARCHAR(255), -- for distributed tracing
    ip_address VARCHAR(45), -- IPv4 or IPv6
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_task ON audit_logs(task_id) WHERE task_id IS NOT NULL;
CREATE INDEX idx_audit_created ON audit_logs(created_at);
CREATE INDEX idx_audit_operation ON audit_logs(operation);
```

**Columns**:
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique log entry identifier |
| task_id | INTEGER | NULLABLE | Associated task (null if deleted) |
| user_id | VARCHAR(255) | FOREIGN KEY → users.id | User who performed operation |
| operation | VARCHAR(20) | NOT NULL | Operation type |
| changes | JSONB | NULLABLE | Before/after values |
| request_id | VARCHAR(255) | NULLABLE | For distributed tracing |
| ip_address | VARCHAR(45) | NULLABLE | Client IP address |
| user_agent | TEXT | NULLABLE | Client user agent |
| created_at | TIMESTAMP | DEFAULT NOW() | When operation occurred |

**Validation Rules**:
- `operation` must be one of: 'created', 'updated', 'completed', 'deleted', 'uncompleted'
- `changes` JSONB format: `{"field": {"old": value, "new": value}}`
- Retention: 90 days (automated cleanup job)

**SQLModel Definition**:
```python
from sqlalchemy import JSON

class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: Optional[int] = Field(default=None, index=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    operation: str = Field(max_length=20, index=True)
    changes: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    request_id: Optional[str] = Field(default=None, max_length=255)
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
```

---

## Entity Relationships

```
users (existing from Phase II)
  ├─── tasks (1:N) - user owns many tasks
  │     ├─── recurring_patterns (1:1) - task has optional recurring pattern
  │     ├─── reminders (1:N) - task has multiple reminders
  │     └─── audit_logs (1:N) - task has audit history
  └─── audit_logs (1:N) - user has audit history
```

**Relationship Details**:
- **User → Tasks**: One-to-Many (user owns multiple tasks)
- **Task → RecurringPattern**: One-to-One (task has at most one recurring pattern)
- **Task → Reminders**: One-to-Many (task can have multiple reminders, e.g., 15 min before, 1 day before)
- **Task → AuditLogs**: One-to-Many (task has complete operation history)
- **User → AuditLogs**: One-to-Many (user has complete operation history)

---

## Kafka Event Schemas

### Topic: `task-events`

**Purpose**: All task CRUD operations

**Event Schema**:
```json
{
  "event_id": "uuid-v4",
  "event_type": "task.created | task.updated | task.completed | task.deleted",
  "task_id": 123,
  "user_id": "user-uuid",
  "timestamp": "2026-01-12T10:30:00Z",
  "task_data": {
    "id": 123,
    "title": "Task title",
    "description": "Task description",
    "completed": false,
    "priority": "high",
    "tags": ["work", "urgent"],
    "due_date": "2026-01-15T14:00:00Z",
    "reminder_offset": 15
  },
  "changes": {
    "priority": {"old": "medium", "new": "high"}
  }
}
```

### Topic: `reminders`

**Purpose**: Scheduled reminder notifications

**Event Schema**:
```json
{
  "event_id": "uuid-v4",
  "event_type": "reminder.due",
  "reminder_id": 456,
  "task_id": 123,
  "user_id": "user-uuid",
  "timestamp": "2026-01-15T13:45:00Z",
  "task_data": {
    "title": "Task title",
    "due_date": "2026-01-15T14:00:00Z"
  }
}
```

### Topic: `task-updates`

**Purpose**: Real-time updates for WebSocket broadcast

**Event Schema**:
```json
{
  "event_id": "uuid-v4",
  "event_type": "task.changed",
  "task_id": 123,
  "user_id": "user-uuid",
  "timestamp": "2026-01-12T10:30:00Z",
  "operation": "updated",
  "task_data": {
    "id": 123,
    "title": "Updated title",
    "completed": false,
    "priority": "high",
    "tags": ["work", "urgent"],
    "due_date": "2026-01-15T14:00:00Z"
  }
}
```

---

## Migration Strategy

### Phase 1: Schema Extensions (Non-Breaking)
```sql
-- Add new columns to tasks table (with defaults, non-breaking)
ALTER TABLE tasks ADD COLUMN priority VARCHAR(10) DEFAULT 'medium';
ALTER TABLE tasks ADD COLUMN tags TEXT[] DEFAULT '{}';
ALTER TABLE tasks ADD COLUMN due_date TIMESTAMP WITH TIME ZONE;
ALTER TABLE tasks ADD COLUMN reminder_offset INTEGER DEFAULT 15;

-- Create indexes
CREATE INDEX idx_tasks_user_priority ON tasks(user_id, priority);
CREATE INDEX idx_tasks_user_due_date ON tasks(user_id, due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_tasks_tags ON tasks USING GIN(tags);
```

### Phase 2: New Tables
```sql
-- Create new tables (no impact on existing data)
CREATE TABLE recurring_patterns (...);
CREATE TABLE reminders (...);
CREATE TABLE audit_logs (...);
```

### Phase 3: Full-Text Search (Optional)
```sql
-- Add search vector column and trigger
ALTER TABLE tasks ADD COLUMN search_vector TSVECTOR;

CREATE OR REPLACE FUNCTION tasks_search_trigger() RETURNS trigger AS $$
BEGIN
  NEW.search_vector :=
    setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'B') ||
    setweight(to_tsvector('english', COALESCE(array_to_string(NEW.tags, ' '), '')), 'C');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tasks_search_update
  BEFORE INSERT OR UPDATE ON tasks
  FOR EACH ROW EXECUTE FUNCTION tasks_search_trigger();

CREATE INDEX idx_tasks_search ON tasks USING GIN(search_vector);
```

### Rollback Plan
- Phase 1: Drop columns (data loss, use with caution)
- Phase 2: Drop tables (no impact on existing tasks)
- Phase 3: Drop trigger and column

---

## Data Integrity Rules

### Cascading Deletes
- Delete user → cascade to tasks, recurring_patterns, reminders, audit_logs
- Delete task → cascade to recurring_patterns, reminders (audit_logs keeps task_id as null)

### Constraints
- User isolation: All queries filter by user_id from JWT
- Unique constraints: recurring_patterns.task_id (one pattern per task)
- Check constraints: priority IN ('high', 'medium', 'low')

### Triggers
- `updated_at` auto-update on tasks, recurring_patterns
- `search_vector` auto-update on tasks (title, description, tags changes)
- Audit log creation on tasks INSERT/UPDATE/DELETE

---

## Performance Considerations

### Indexes
- **User isolation**: `user_id` indexed on all tables
- **Search/filter**: Composite indexes on `(user_id, priority)`, `(user_id, due_date)`
- **Tags**: GIN index for array containment queries
- **Full-text search**: GIN index on `search_vector`
- **Reminders**: Partial index on `(remind_at, sent)` WHERE sent=FALSE

### Query Optimization
- Use `EXPLAIN ANALYZE` to verify index usage
- Limit result sets (pagination with LIMIT/OFFSET)
- Avoid N+1 queries (use JOINs or eager loading)
- Cache frequently accessed data (user preferences, tag lists)

### Scaling
- Neon Serverless auto-scales connections
- Read replicas for reporting queries (if needed)
- Partition audit_logs by month (if >1M rows)

---

## Summary

**New Tables**: 3 (recurring_patterns, reminders, audit_logs)
**Extended Tables**: 1 (tasks with 5 new columns)
**New Indexes**: 8 (performance-critical queries)
**Kafka Topics**: 3 (task-events, reminders, task-updates)
**Backward Compatible**: Yes (all new columns have defaults)
**Migration Risk**: Low (additive changes only)
