"""
Prometheus metrics endpoint for Notification Service

This module exposes Prometheus metrics for monitoring notification service operations.
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import APIRouter, Response
import time

# Create metrics router
router = APIRouter(prefix="/metrics", tags=["metrics"])

# Metrics definitions
notifications_sent_total = Counter(
    'notifications_sent_total',
    'Total number of notifications sent',
    ['notification_type', 'channel']
)

notifications_failed_total = Counter(
    'notifications_failed_total',
    'Total number of failed notifications',
    ['notification_type', 'channel', 'error_type']
)

notification_processing_duration = Histogram(
    'notification_processing_duration_seconds',
    'Time spent processing notifications',
    ['notification_type', 'channel'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

notification_queue_size = Gauge(
    'notification_queue_size',
    'Current size of notification queue',
    ['priority']
)

notification_retry_count = Counter(
    'notification_retry_count_total',
    'Total number of notification retries',
    ['notification_type', 'channel']
)

email_notifications_sent = Counter(
    'email_notifications_sent_total',
    'Total number of email notifications sent',
    ['template']
)

push_notifications_sent = Counter(
    'push_notifications_sent_total',
    'Total number of push notifications sent',
    ['platform']
)

sms_notifications_sent = Counter(
    'sms_notifications_sent_total',
    'Total number of SMS notifications sent'
)

notification_delivery_rate = Gauge(
    'notification_delivery_rate',
    'Current notification delivery success rate',
    ['notification_type']
)

active_notification_workers = Gauge(
    'active_notification_workers',
    'Number of active notification worker threads'
)


class MetricsCollector:
    """Helper class for collecting and updating metrics"""

    @staticmethod
    def record_notification_sent(notification_type: str, channel: str):
        """Record a successful notification send"""
        notifications_sent_total.labels(
            notification_type=notification_type,
            channel=channel
        ).inc()

    @staticmethod
    def record_notification_failed(notification_type: str, channel: str, error_type: str):
        """Record a failed notification"""
        notifications_failed_total.labels(
            notification_type=notification_type,
            channel=channel,
            error_type=error_type
        ).inc()

    @staticmethod
    def record_processing_time(notification_type: str, channel: str, duration: float):
        """Record notification processing duration"""
        notification_processing_duration.labels(
            notification_type=notification_type,
            channel=channel
        ).observe(duration)

    @staticmethod
    def update_queue_size(priority: str, size: int):
        """Update notification queue size"""
        notification_queue_size.labels(priority=priority).set(size)

    @staticmethod
    def record_retry(notification_type: str, channel: str):
        """Record a notification retry"""
        notification_retry_count.labels(
            notification_type=notification_type,
            channel=channel
        ).inc()

    @staticmethod
    def record_email_sent(template: str):
        """Record an email notification sent"""
        email_notifications_sent.labels(template=template).inc()

    @staticmethod
    def record_push_sent(platform: str):
        """Record a push notification sent"""
        push_notifications_sent.labels(platform=platform).inc()

    @staticmethod
    def record_sms_sent():
        """Record an SMS notification sent"""
        sms_notifications_sent.inc()

    @staticmethod
    def update_delivery_rate(notification_type: str, rate: float):
        """Update notification delivery success rate"""
        notification_delivery_rate.labels(notification_type=notification_type).set(rate)

    @staticmethod
    def update_active_workers(count: int):
        """Update active worker count"""
        active_notification_workers.set(count)


@router.get("")
async def metrics():
    """
    Prometheus metrics endpoint

    Returns metrics in Prometheus text format for scraping
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


# Export metrics collector for use in service
__all__ = ['router', 'MetricsCollector']
