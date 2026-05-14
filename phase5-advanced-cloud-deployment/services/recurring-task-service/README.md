# Recurring Task Service

Microservice responsible for automatically creating next occurrences of recurring tasks.

## Features

- Subscribes to `task-events` Kafka topic via Dapr
- Listens for `task.completed` events
- Automatically calculates and creates next occurrence for recurring tasks
- Supports daily, weekly, monthly, and yearly recurrence patterns
- Publishes `recurring.task.created` events

## Event Schema

### Input: Task Completed Event
```json
{
  "event_type": "task.completed",
  "task_id": "uuid",
  "user_id": "uuid",
  "task_data": {
    "title": "Weekly team meeting",
    "recurring_type": "weekly",
    "due_date": "2024-01-20T10:00:00Z",
    "priority": "high"
  }
}
```

### Output: Recurring Task Created Event
```json
{
  "event_type": "recurring.task.created",
  "user_id": "uuid",
  "original_task_id": "uuid",
  "task_data": {
    "title": "Weekly team meeting",
    "due_date": "2024-01-27T10:00:00Z",
    "recurring_type": "weekly",
    "status": "pending"
  },
  "created_at": "2024-01-20T10:05:00Z",
  "service": "recurring-task-service"
}
```

## Recurrence Patterns

- **Daily**: Creates next occurrence 1 day after completion
- **Weekly**: Creates next occurrence 1 week after completion
- **Monthly**: Creates next occurrence ~30 days after completion
- **Yearly**: Creates next occurrence 365 days after completion

## Endpoints

- `GET /health` - Health check
- `POST /events/task-events` - Dapr subscription endpoint

## Environment Variables

- `SERVICE_NAME` - Service identifier (default: recurring-task-service)
- `DAPR_HTTP_PORT` - Dapr sidecar HTTP port (default: 3500)
- `DAPR_PUBSUB_NAME` - Dapr pub/sub component name (default: pubsub-kafka)
- `PORT` - Service port (default: 8002)

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run service
python src/main.py
```

## Docker Build

```bash
docker build -t recurring-task-service:latest .
docker run -p 8002:8002 recurring-task-service:latest
```
