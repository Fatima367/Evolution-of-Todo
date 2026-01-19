# Kafka Topics and Event Schemas

## Overview

TodoBoard uses Kafka (via Dapr pub/sub) for asynchronous event processing and real-time updates. This document describes all Kafka topics, event types, and their schemas.

## Topics

### 1. task-events

**Purpose**: Complete audit trail of all task operations

**Consumers**: Audit Service

**Partitioning**: By `user_id` to guarantee event ordering per user

**Retention**: 30 days (configurable)

**Event Types**:
- `task.created`
- `task.updated`
- `task.completed`
- `task.deleted`

---

### 2. task-updates

**Purpose**: Real-time task changes for WebSocket broadcast

**Consumers**: WebSocket Service (Backend API)

**Partitioning**: By `user_id` to guarantee event ordering per user

**Retention**: 24 hours (short retention for real-time updates)

**Event Types**:
- `task.changed`

---

### 3. reminders

**Purpose**: Scheduled reminder notifications

**Consumers**: Notification Service

**Partitioning**: By `user_id` to guarantee event ordering per user

**Retention**: 7 days

**Event Types**:
- `reminder.due`

---

### 4. dead-letter-queue

**Purpose**: Failed events for investigation and retry

**Consumers**: Manual investigation, monitoring alerts

**Partitioning**: None (single partition)

**Retention**: 90 days (long retention for forensics)

**Event Types**:
- Any failed event from other topics

---

## Event Schemas

### Common Fields

All events include these common fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `event_id` | `string` (UUID) | Yes | Unique identifier for this event |
| `event_type` | `string` | Yes | Type of event (e.g., "task.created") |
| `timestamp` | `string` (ISO 8601) | Yes | When the event occurred (UTC) |
| `user_id` | `string` (UUID) | Yes | User who triggered the event |
| `request_id` | `string` (UUID) | No | Request ID for distributed tracing |

---

## Event Type: task.created

**Topic**: `task-events`

**Description**: Published when a new task is created

**Schema**:

```json
{
  "event_id": "string (UUID)",
  "event_type": "task.created",
  "task_id": "string (UUID)",
  "user_id": "string (UUID)",
  "timestamp": "string (ISO 8601)",
  "task_data": {
    "id": "string (UUID)",
    "user_id": "string (UUID)",
    "title": "string",
    "description": "string | null",
    "completed": "boolean",
    "priority": "string (low|medium|high)",
    "tags": "array of strings",
    "due_date": "string (ISO 8601) | null",
    "reminder_offset": "integer | null",
    "is_favorite": "boolean",
    "recurring_type": "string | null",
    "created_at": "string (ISO 8601)",
    "updated_at": "string (ISO 8601)"
  },
  "request_id": "string (UUID) | null"
}
```

**Example**:

```json
{
  "event_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "event_type": "task.created",
  "task_id": "12345678-1234-1234-1234-123456789012",
  "user_id": "87654321-4321-4321-4321-210987654321",
  "timestamp": "2026-01-19T10:30:00.000Z",
  "task_data": {
    "id": "12345678-1234-1234-1234-123456789012",
    "user_id": "87654321-4321-4321-4321-210987654321",
    "title": "Complete project documentation",
    "description": "Write comprehensive docs for Phase V",
    "completed": false,
    "priority": "high",
    "tags": ["documentation", "phase5", "urgent"],
    "due_date": "2026-01-20T17:00:00.000Z",
    "reminder_offset": 900,
    "is_favorite": true,
    "recurring_type": null,
    "created_at": "2026-01-19T10:30:00.000Z",
    "updated_at": "2026-01-19T10:30:00.000Z"
  },
  "request_id": "req-a1b2c3d4-e5f6-7890"
}
```

---

## Event Type: task.updated

**Topic**: `task-events`

**Description**: Published when a task is modified

**Schema**:

```json
{
  "event_id": "string (UUID)",
  "event_type": "task.updated",
  "task_id": "string (UUID)",
  "user_id": "string (UUID)",
  "timestamp": "string (ISO 8601)",
  "task_data": {
    "id": "string (UUID)",
    "user_id": "string (UUID)",
    "title": "string",
    "description": "string | null",
    "completed": "boolean",
    "priority": "string (low|medium|high)",
    "tags": "array of strings",
    "due_date": "string (ISO 8601) | null",
    "reminder_offset": "integer | null",
    "is_favorite": "boolean",
    "recurring_type": "string | null",
    "created_at": "string (ISO 8601)",
    "updated_at": "string (ISO 8601)"
  },
  "changes": {
    "field_name": {
      "old": "any",
      "new": "any"
    }
  },
  "request_id": "string (UUID) | null"
}
```

**Example**:

```json
{
  "event_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "event_type": "task.updated",
  "task_id": "12345678-1234-1234-1234-123456789012",
  "user_id": "87654321-4321-4321-4321-210987654321",
  "timestamp": "2026-01-19T11:45:00.000Z",
  "task_data": {
    "id": "12345678-1234-1234-1234-123456789012",
    "user_id": "87654321-4321-4321-4321-210987654321",
    "title": "Complete project documentation",
    "description": "Write comprehensive docs for Phase V - Updated with event schemas",
    "completed": false,
    "priority": "high",
    "tags": ["documentation", "phase5", "urgent", "kafka"],
    "due_date": "2026-01-20T17:00:00.000Z",
    "reminder_offset": 900,
    "is_favorite": true,
    "recurring_type": null,
    "created_at": "2026-01-19T10:30:00.000Z",
    "updated_at": "2026-01-19T11:45:00.000Z"
  },
  "changes": {
    "description": {
      "old": "Write comprehensive docs for Phase V",
      "new": "Write comprehensive docs for Phase V - Updated with event schemas"
    },
    "tags": {
      "old": ["documentation", "phase5", "urgent"],
      "new": ["documentation", "phase5", "urgent", "kafka"]
    }
  },
  "request_id": "req-b2c3d4e5-f6a7-8901"
}
```

---

## Event Type: task.completed

**Topic**: `task-events`

**Description**: Published when a task is marked as complete

**Schema**:

```json
{
  "event_id": "string (UUID)",
  "event_type": "task.completed",
  "task_id": "string (UUID)",
  "user_id": "string (UUID)",
  "timestamp": "string (ISO 8601)",
  "task_data": {
    "id": "string (UUID)",
    "user_id": "string (UUID)",
    "title": "string",
    "description": "string | null",
    "completed": "boolean",
    "priority": "string (low|medium|high)",
    "tags": "array of strings",
    "due_date": "string (ISO 8601) | null",
    "reminder_offset": "integer | null",
    "is_favorite": "boolean",
    "recurring_type": "string | null",
    "created_at": "string (ISO 8601)",
    "updated_at": "string (ISO 8601)",
    "completed_at": "string (ISO 8601)"
  },
  "request_id": "string (UUID) | null"
}
```

**Example**:

```json
{
  "event_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
  "event_type": "task.completed",
  "task_id": "12345678-1234-1234-1234-123456789012",
  "user_id": "87654321-4321-4321-4321-210987654321",
  "timestamp": "2026-01-19T16:30:00.000Z",
  "task_data": {
    "id": "12345678-1234-1234-1234-123456789012",
    "user_id": "87654321-4321-4321-4321-210987654321",
    "title": "Complete project documentation",
    "description": "Write comprehensive docs for Phase V - Updated with event schemas",
    "completed": true,
    "priority": "high",
    "tags": ["documentation", "phase5", "urgent", "kafka"],
    "due_date": "2026-01-20T17:00:00.000Z",
    "reminder_offset": 900,
    "is_favorite": true,
    "recurring_type": null,
    "created_at": "2026-01-19T10:30:00.000Z",
    "updated_at": "2026-01-19T16:30:00.000Z",
    "completed_at": "2026-01-19T16:30:00.000Z"
  },
  "request_id": "req-c3d4e5f6-a7b8-9012"
}
```

**Note**: This event triggers the Recurring Task Service to check if a new instance should be created.

---

## Event Type: task.deleted

**Topic**: `task-events`

**Description**: Published when a task is deleted

**Schema**:

```json
{
  "event_id": "string (UUID)",
  "event_type": "task.deleted",
  "task_id": "string (UUID)",
  "user_id": "string (UUID)",
  "timestamp": "string (ISO 8601)",
  "task_data": {
    "id": "string (UUID)",
    "user_id": "string (UUID)",
    "title": "string",
    "description": "string | null",
    "completed": "boolean",
    "priority": "string (low|medium|high)",
    "tags": "array of strings",
    "due_date": "string (ISO 8601) | null",
    "reminder_offset": "integer | null",
    "is_favorite": "boolean",
    "recurring_type": "string | null",
    "created_at": "string (ISO 8601)",
    "updated_at": "string (ISO 8601)"
  },
  "request_id": "string (UUID) | null"
}
```

**Example**:

```json
{
  "event_id": "d4e5f6a7-b8c9-0123-def1-234567890123",
  "event_type": "task.deleted",
  "task_id": "98765432-9876-9876-9876-987654321098",
  "user_id": "87654321-4321-4321-4321-210987654321",
  "timestamp": "2026-01-19T17:00:00.000Z",
  "task_data": {
    "id": "98765432-9876-9876-9876-987654321098",
    "user_id": "87654321-4321-4321-4321-210987654321",
    "title": "Old task to be removed",
    "description": "This task is no longer needed",
    "completed": false,
    "priority": "low",
    "tags": ["cleanup"],
    "due_date": null,
    "reminder_offset": null,
    "is_favorite": false,
    "recurring_type": null,
    "created_at": "2026-01-15T10:00:00.000Z",
    "updated_at": "2026-01-15T10:00:00.000Z"
  },
  "request_id": "req-d4e5f6a7-b8c9-0123"
}
```

---

## Event Type: task.changed

**Topic**: `task-updates`

**Description**: Published for real-time WebSocket broadcast to connected clients

**Schema**:

```json
{
  "event_id": "string (UUID)",
  "event_type": "task.changed",
  "task_id": "string (UUID)",
  "user_id": "string (UUID)",
  "timestamp": "string (ISO 8601)",
  "operation": "string (created|updated|completed|deleted)",
  "task_data": {
    "id": "string (UUID)",
    "user_id": "string (UUID)",
    "title": "string",
    "description": "string | null",
    "completed": "boolean",
    "priority": "string (low|medium|high)",
    "tags": "array of strings",
    "due_date": "string (ISO 8601) | null",
    "reminder_offset": "integer | null",
    "is_favorite": "boolean",
    "recurring_type": "string | null",
    "created_at": "string (ISO 8601)",
    "updated_at": "string (ISO 8601)"
  }
}
```

**Example**:

```json
{
  "event_id": "e5f6a7b8-c9d0-1234-ef12-345678901234",
  "event_type": "task.changed",
  "task_id": "12345678-1234-1234-1234-123456789012",
  "user_id": "87654321-4321-4321-4321-210987654321",
  "timestamp": "2026-01-19T11:45:00.000Z",
  "operation": "updated",
  "task_data": {
    "id": "12345678-1234-1234-1234-123456789012",
    "user_id": "87654321-4321-4321-4321-210987654321",
    "title": "Complete project documentation",
    "description": "Write comprehensive docs for Phase V - Updated with event schemas",
    "completed": false,
    "priority": "high",
    "tags": ["documentation", "phase5", "urgent", "kafka"],
    "due_date": "2026-01-20T17:00:00.000Z",
    "reminder_offset": 900,
    "is_favorite": true,
    "recurring_type": null,
    "created_at": "2026-01-19T10:30:00.000Z",
    "updated_at": "2026-01-19T11:45:00.000Z"
  }
}
```

**Note**: This event is consumed by the WebSocket service and broadcast to all connected clients for the user.

---

## Event Type: reminder.due

**Topic**: `reminders`

**Description**: Published when a reminder is due for a task

**Schema**:

```json
{
  "event_id": "string (UUID)",
  "event_type": "reminder.due",
  "reminder_id": "integer",
  "task_id": "string (UUID)",
  "user_id": "string (UUID)",
  "timestamp": "string (ISO 8601)",
  "task_data": {
    "title": "string",
    "due_date": "string (ISO 8601) | null"
  },
  "request_id": "string (UUID) | null"
}
```

**Example**:

```json
{
  "event_id": "f6a7b8c9-d0e1-2345-f123-456789012345",
  "event_type": "reminder.due",
  "reminder_id": 42,
  "task_id": "12345678-1234-1234-1234-123456789012",
  "user_id": "87654321-4321-4321-4321-210987654321",
  "timestamp": "2026-01-20T16:45:00.000Z",
  "task_data": {
    "title": "Complete project documentation",
    "due_date": "2026-01-20T17:00:00.000Z"
  },
  "request_id": "req-f6a7b8c9-d0e1-2345"
}
```

**Note**: This event is consumed by the Notification Service to send reminders to users.

---

## Dead Letter Queue Event

**Topic**: `dead-letter-queue`

**Description**: Failed events that could not be processed after retries

**Schema**:

```json
{
  "dlq_id": "string (UUID)",
  "original_topic": "string",
  "original_event": {
    "...": "original event data"
  },
  "error_message": "string",
  "failed_at": "string (ISO 8601)",
  "retry_count": "integer"
}
```

**Example**:

```json
{
  "dlq_id": "a7b8c9d0-e1f2-3456-a123-567890123456",
  "original_topic": "reminders",
  "original_event": {
    "event_id": "f6a7b8c9-d0e1-2345-f123-456789012345",
    "event_type": "reminder.due",
    "reminder_id": 42,
    "task_id": "12345678-1234-1234-1234-123456789012",
    "user_id": "87654321-4321-4321-4321-210987654321",
    "timestamp": "2026-01-20T16:45:00.000Z",
    "task_data": {
      "title": "Complete project documentation",
      "due_date": "2026-01-20T17:00:00.000Z"
    }
  },
  "error_message": "Failed to send notification: Connection timeout",
  "failed_at": "2026-01-20T16:45:30.000Z",
  "retry_count": 3
}
```

---

## Event Reliability

### Event Ordering

Events are partitioned by `user_id` to guarantee ordering:
- All events for a specific user are sent to the same partition
- Kafka guarantees order within a partition
- Consumers process events in order per user

### At-Least-Once Delivery

- Producers retry failed publishes with exponential backoff
- Consumers use manual commit after successful processing
- Failed events are sent to dead letter queue after max retries

### Error Handling

1. **Transient Errors**: Retry with exponential backoff (3 attempts)
2. **Permanent Errors**: Send to dead letter queue immediately
3. **Dead Letter Queue**: Manual investigation and replay

### Monitoring

- **Kafka Lag**: Monitor consumer lag per topic
- **Event Rate**: Track events published/consumed per second
- **Error Rate**: Track failed events and DLQ entries
- **Processing Time**: Histogram of event processing duration

---

## Event Publishing

### From Backend API

```python
from src.services.event_publisher import event_publisher

# Publish task created event
await event_publisher.publish_task_created(
    task_id=task.id,
    user_id=current_user.id,
    task_data=task.dict(),
    request_id=request_id
)
```

### Metadata

All events include metadata for partitioning:

```python
metadata = {
    "user_id": str(user_id)  # Partition key
}
```

---

## Event Consumption

### Consumer Configuration

```python
# Example consumer configuration
consumer_config = {
    "bootstrap_servers": "kafka:9092",
    "group_id": "audit-service",
    "auto_offset_reset": "earliest",
    "enable_auto_commit": False,  # Manual commit
    "max_poll_records": 100,
    "session_timeout_ms": 30000
}
```

### Processing Pattern

```python
async def process_event(event):
    try:
        # Process event
        await handle_event(event)

        # Commit offset on success
        await consumer.commit()

    except Exception as e:
        logger.error(f"Failed to process event: {e}")
        # Retry or send to DLQ
```

---

## Testing Events

### Local Testing with Kafka

```bash
# Produce test event
echo '{"event_type":"task.created","task_id":"test-123"}' | \
  kafka-console-producer --broker-list localhost:9092 --topic task-events

# Consume events
kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic task-events --from-beginning
```

### Integration Tests

```python
import pytest
from src.services.event_publisher import event_publisher

@pytest.mark.asyncio
async def test_publish_task_created():
    # Publish event
    await event_publisher.publish_task_created(
        task_id=uuid4(),
        user_id=uuid4(),
        task_data={"title": "Test Task"}
    )

    # Verify event in Kafka
    # (implementation depends on test setup)
```

---

## References

- [Architecture Documentation](./architecture.md)
- [Dapr Pub/Sub Documentation](./dapr-setup.md)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Event-Driven Architecture Best Practices](https://www.confluent.io/blog/event-driven-architecture-best-practices/)
