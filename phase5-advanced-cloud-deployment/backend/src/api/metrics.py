"""Prometheus metrics endpoint for backend API"""
from fastapi import APIRouter
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import time

router = APIRouter(tags=["metrics"])

# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Task metrics
tasks_created_total = Counter(
    'tasks_created_total',
    'Total tasks created',
    ['user_id']
)

tasks_completed_total = Counter(
    'tasks_completed_total',
    'Total tasks completed',
    ['user_id']
)

tasks_deleted_total = Counter(
    'tasks_deleted_total',
    'Total tasks deleted',
    ['user_id']
)

active_tasks_gauge = Gauge(
    'active_tasks',
    'Number of active tasks',
    ['user_id', 'priority']
)

# Event metrics
events_published_total = Counter(
    'events_published_total',
    'Total events published',
    ['topic', 'event_type']
)

events_failed_total = Counter(
    'events_failed_total',
    'Total events that failed to publish',
    ['topic', 'event_type']
)

# Database metrics
db_connections_active = Gauge(
    'db_connections_active',
    'Number of active database connections'
)

db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type']
)

# WebSocket metrics
websocket_connections_active = Gauge(
    'websocket_connections_active',
    'Number of active WebSocket connections'
)

websocket_messages_sent_total = Counter(
    'websocket_messages_sent_total',
    'Total WebSocket messages sent',
    ['message_type']
)


@router.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint

    Returns metrics in Prometheus text format for scraping.
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


# Middleware for automatic request tracking
class MetricsMiddleware:
    """Middleware to track HTTP request metrics"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope["method"]
        path = scope["path"]

        start_time = time.time()

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status = message["status"]
                duration = time.time() - start_time

                # Record metrics
                http_requests_total.labels(
                    method=method,
                    endpoint=path,
                    status=status
                ).inc()

                http_request_duration_seconds.labels(
                    method=method,
                    endpoint=path
                ).observe(duration)

            await send(message)

        await self.app(scope, receive, send_wrapper)
