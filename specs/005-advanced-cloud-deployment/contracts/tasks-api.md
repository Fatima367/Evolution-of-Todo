# API Contract: Tasks Extended Endpoints

**Feature**: 005-advanced-cloud-deployment
**Version**: 2.0.0
**Base URL**: `/api/v1`
**Authentication**: Bearer JWT token (Better Auth)

## Extended Task Endpoints

### GET /tasks

**Description**: List tasks with advanced filtering, sorting, and search

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| priority | string | No | Filter by priority: high, medium, low |
| tags | string[] | No | Filter by tags (comma-separated) |
| completed | boolean | No | Filter by completion status |
| due_before | datetime | No | Filter tasks due before this date |
| due_after | datetime | No | Filter tasks due after this date |
| search | string | No | Full-text search in title, description, tags |
| sort_by | string | No | Sort field: due_date, priority, created_at, updated_at |
| sort_order | string | No | Sort order: asc, desc (default: asc) |
| limit | integer | No | Page size (default: 50, max: 100) |
| offset | integer | No | Pagination offset (default: 0) |

**Response**: 200 OK
```json
{
  "tasks": [
    {
      "id": 123,
      "user_id": "user-uuid",
      "title": "Complete project proposal",
      "description": "Draft and submit Q1 proposal",
      "completed": false,
      "priority": "high",
      "tags": ["work", "urgent"],
      "due_date": "2026-01-15T14:00:00Z",
      "reminder_offset": 15,
      "created_at": "2026-01-10T09:00:00Z",
      "updated_at": "2026-01-12T10:30:00Z"
    }
  ],
  "total": 42,
  "limit": 50,
  "offset": 0
}
```

**Errors**:
- 400 Bad Request: Invalid query parameters
- 401 Unauthorized: Missing or invalid JWT token
- 500 Internal Server Error: Database error

---

### POST /tasks

**Description**: Create a new task with advanced features

**Request Body**:
```json
{
  "title": "Complete project proposal",
  "description": "Draft and submit Q1 proposal",
  "priority": "high",
  "tags": ["work", "urgent"],
  "due_date": "2026-01-15T14:00:00Z",
  "reminder_offset": 15
}
```

**Validation**:
- `title`: Required, max 255 characters
- `description`: Optional, max 10,000 characters
- `priority`: Optional, one of: high, medium, low (default: medium)
- `tags`: Optional, array of strings, max 10 tags, each max 50 characters
- `due_date`: Optional, ISO 8601 datetime, must be in future
- `reminder_offset`: Optional, integer 0-1440 (default: 15)

**Response**: 201 Created
```json
{
  "id": 123,
  "user_id": "user-uuid",
  "title": "Complete project proposal",
  "description": "Draft and submit Q1 proposal",
  "completed": false,
  "priority": "high",
  "tags": ["work", "urgent"],
  "due_date": "2026-01-15T14:00:00Z",
  "reminder_offset": 15,
  "created_at": "2026-01-12T10:30:00Z",
  "updated_at": "2026-01-12T10:30:00Z"
}
```

**Side Effects**:
- Publishes `task.created` event to Kafka `task-events` topic
- Creates reminder if `due_date` is set
- Publishes `task.changed` event to Kafka `task-updates` topic (for WebSocket broadcast)

**Errors**:
- 400 Bad Request: Validation error
- 401 Unauthorized: Missing or invalid JWT token
- 500 Internal Server Error: Database or Kafka error

---

### PATCH /tasks/{task_id}

**Description**: Update task with partial fields

**Path Parameters**:
- `task_id`: integer, required

**Request Body** (all fields optional):
```json
{
  "title": "Updated title",
  "description": "Updated description",
  "completed": true,
  "priority": "medium",
  "tags": ["work"],
  "due_date": "2026-01-20T14:00:00Z",
  "reminder_offset": 30
}
```

**Response**: 200 OK
```json
{
  "id": 123,
  "user_id": "user-uuid",
  "title": "Updated title",
  "description": "Updated description",
  "completed": true,
  "priority": "medium",
  "tags": ["work"],
  "due_date": "2026-01-20T14:00:00Z",
  "reminder_offset": 30,
  "created_at": "2026-01-12T10:30:00Z",
  "updated_at": "2026-01-12T11:00:00Z"
}
```

**Side Effects**:
- Publishes `task.updated` or `task.completed` event to Kafka `task-events` topic
- Updates or creates reminder if `due_date` changed
- Publishes `task.changed` event to Kafka `task-updates` topic
- If recurring task completed, triggers next occurrence creation

**Errors**:
- 400 Bad Request: Validation error
- 401 Unauthorized: Missing or invalid JWT token
- 403 Forbidden: Task belongs to different user
- 404 Not Found: Task not found
- 500 Internal Server Error: Database or Kafka error

---

## Recurring Task Endpoints

### POST /tasks/{task_id}/recurring

**Description**: Make a task recurring

**Path Parameters**:
- `task_id`: integer, required

**Request Body**:
```json
{
  "frequency": "weekly",
  "interval": 1,
  "day_of_week": 1,
  "end_date": "2026-12-31T23:59:59Z"
}
```

**Validation**:
- `frequency`: Required, one of: daily, weekly, monthly, yearly, custom
- `interval`: Optional, integer >= 1 (default: 1)
- `day_of_week`: Required if frequency=weekly, integer 0-6 (0=Monday)
- `day_of_month`: Required if frequency=monthly, integer 1-31
- `month_of_year`: Required if frequency=yearly, integer 1-12
- `end_date`: Optional, ISO 8601 datetime, must be after task.due_date

**Response**: 201 Created
```json
{
  "id": 456,
  "task_id": 123,
  "user_id": "user-uuid",
  "frequency": "weekly",
  "interval": 1,
  "day_of_week": 1,
  "end_date": "2026-12-31T23:59:59Z",
  "last_generated_at": null,
  "created_at": "2026-01-12T10:30:00Z",
  "updated_at": "2026-01-12T10:30:00Z"
}
```

**Errors**:
- 400 Bad Request: Validation error or task already recurring
- 401 Unauthorized: Missing or invalid JWT token
- 403 Forbidden: Task belongs to different user
- 404 Not Found: Task not found
- 500 Internal Server Error: Database error

---

### DELETE /tasks/{task_id}/recurring

**Description**: Remove recurring pattern from task

**Path Parameters**:
- `task_id`: integer, required

**Response**: 204 No Content

**Errors**:
- 401 Unauthorized: Missing or invalid JWT token
- 403 Forbidden: Task belongs to different user
- 404 Not Found: Task or recurring pattern not found
- 500 Internal Server Error: Database error

---

## Reminder Endpoints

### GET /tasks/{task_id}/reminders

**Description**: List reminders for a task

**Path Parameters**:
- `task_id`: integer, required

**Response**: 200 OK
```json
{
  "reminders": [
    {
      "id": 789,
      "task_id": 123,
      "user_id": "user-uuid",
      "remind_at": "2026-01-15T13:45:00Z",
      "sent": false,
      "sent_at": null,
      "created_at": "2026-01-12T10:30:00Z"
    }
  ]
}
```

**Errors**:
- 401 Unauthorized: Missing or invalid JWT token
- 403 Forbidden: Task belongs to different user
- 404 Not Found: Task not found
- 500 Internal Server Error: Database error

---

## WebSocket Endpoint

### WS /ws/tasks

**Description**: Real-time task updates via WebSocket

**Authentication**: JWT token in query parameter `?token=<jwt>`

**Connection**:
```javascript
const ws = new WebSocket('wss://api.example.com/ws/tasks?token=<jwt>');
```

**Message Format** (server → client):
```json
{
  "event_type": "task.changed",
  "task_id": 123,
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

**Event Types**:
- `task.changed`: Task created, updated, or deleted
- `connection.established`: Connection successful
- `connection.error`: Connection error

**Client Actions**:
- Send ping every 30 seconds to keep connection alive
- Reconnect on disconnect with exponential backoff

**Errors**:
- 401 Unauthorized: Invalid JWT token
- 403 Forbidden: Token expired
- 500 Internal Server Error: WebSocket server error
