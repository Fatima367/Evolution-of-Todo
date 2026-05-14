# Notification Service

Microservice responsible for handling task reminder notifications.

## Features

- Subscribes to `reminders` Kafka topic via Dapr
- Sends notifications when reminders are due
- Publishes `notification.sent` events for audit trail
- Health check endpoint for Kubernetes probes

## Event Schema

### Input: Reminder Event
```json
{
  "task_id": "uuid",
  "user_id": "uuid",
  "title": "Task title",
  "due_at": "2024-01-20T10:00:00Z",
  "remind_at": "2024-01-20T09:45:00Z"
}
```

### Output: Notification Sent Event
```json
{
  "event_type": "notification.sent",
  "task_id": "uuid",
  "user_id": "uuid",
  "notification_type": "reminder",
  "sent_at": "2024-01-20T09:45:00Z",
  "service": "notification-service"
}
```

## Endpoints

- `GET /health` - Health check
- `POST /events/reminders` - Dapr subscription endpoint

## Environment Variables

- `SERVICE_NAME` - Service identifier (default: notification-service)
- `DAPR_HTTP_PORT` - Dapr sidecar HTTP port (default: 3500)
- `DAPR_PUBSUB_NAME` - Dapr pub/sub component name (default: pubsub-kafka)
- `PORT` - Service port (default: 8001)

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run service
python src/main.py
```

## Docker Build

```bash
docker build -t notification-service:latest .
docker run -p 8001:8001 notification-service:latest
```

## Integration Points

In production, integrate with:
- Email service (SendGrid, AWS SES)
- SMS service (Twilio)
- Push notifications (Firebase, OneSignal)
- In-app notifications
