# Audit Service

Microservice responsible for logging all task operations for audit trail and compliance.

## Features

- Subscribes to `task-events` Kafka topic via Dapr
- Logs all task CRUD operations (create, update, delete, complete)
- Stores audit logs in PostgreSQL via Dapr state store
- Provides audit trail for compliance and debugging
- Health check endpoint for Kubernetes probes

## Event Schema

### Input: Task Event
```json
{
  "event_type": "task.created|task.updated|task.completed|task.deleted",
  "task_id": "uuid",
  "user_id": "uuid",
  "task_data": {
    "title": "Task title",
    "status": "completed",
    "priority": "high"
  },
  "timestamp": "2024-01-20T10:00:00Z"
}
```

### Stored Audit Log
```json
{
  "audit_id": "task-uuid_timestamp",
  "event_type": "task.completed",
  "task_id": "uuid",
  "user_id": "uuid",
  "task_data": {...},
  "timestamp": "2024-01-20T10:00:00Z",
  "service": "audit-service"
}
```

## Endpoints

- `GET /health` - Health check
- `POST /events/task-events` - Dapr subscription endpoint
- `GET /audit-logs/{user_id}` - Get audit logs for user (placeholder)
- `GET /stats` - Get audit statistics (placeholder)

## Environment Variables

- `SERVICE_NAME` - Service identifier (default: audit-service)
- `DAPR_HTTP_PORT` - Dapr sidecar HTTP port (default: 3500)
- `DAPR_PUBSUB_NAME` - Dapr pub/sub component name (default: pubsub-kafka)
- `DAPR_STATE_STORE` - Dapr state store name (default: statestore-postgres)
- `PORT` - Service port (default: 8003)

## Storage

Audit logs are stored in PostgreSQL via Dapr state store with keys:
```
audit:{user_id}:{audit_id}
```

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run service
python src/main.py
```

## Docker Build

```bash
docker build -t audit-service:latest .
docker run -p 8003:8003 audit-service:latest
```

## Use Cases

1. **Compliance**: Track all changes to tasks for regulatory compliance
2. **Debugging**: Investigate issues by reviewing task operation history
3. **Analytics**: Analyze user behavior and task patterns
4. **Security**: Detect suspicious activity or unauthorized access
