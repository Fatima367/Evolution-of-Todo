"""
Prometheus metrics endpoint for Audit Service

This module exposes Prometheus metrics for monitoring audit logging operations.
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import APIRouter, Response
import time

# Create metrics router
router = APIRouter(prefix="/metrics", tags=["metrics"])

# Metrics definitions
audit_events_total = Counter(
    'audit_events_total',
    'Total number of audit events logged',
    ['event_type', 'resource_type', 'action']
)

audit_events_failed_total = Counter(
    'audit_events_failed_total',
    'Total number of failed audit event writes',
    ['event_type', 'error_type']
)

audit_event_processing_duration = Histogram(
    'audit_event_processing_duration_seconds',
    'Time spent processing audit events',
    ['event_type'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0]
)

audit_storage_size_bytes = Gauge(
    'audit_storage_size_bytes',
    'Current size of audit log storage in bytes'
)

audit_events_by_user = Counter(
    'audit_events_by_user_total',
    'Total number of audit events by user',
    ['user_id', 'action']
)

audit_events_by_resource = Counter(
    'audit_events_by_resource_total',
    'Total number of audit events by resource',
    ['resource_type', 'action']
)

audit_query_duration = Histogram(
    'audit_query_duration_seconds',
    'Time spent querying audit logs',
    ['query_type'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

audit_retention_violations = Counter(
    'audit_retention_violations_total',
    'Total number of audit retention policy violations detected',
    ['violation_type']
)

audit_compliance_checks = Counter(
    'audit_compliance_checks_total',
    'Total number of compliance checks performed',
    ['check_type', 'result']
)

audit_event_queue_size = Gauge(
    'audit_event_queue_size',
    'Current size of audit event processing queue'
)

audit_batch_size = Histogram(
    'audit_batch_size',
    'Size of audit event batches written to storage',
    buckets=[1, 5, 10, 25, 50, 100, 250, 500]
)

audit_sensitive_events_total = Counter(
    'audit_sensitive_events_total',
    'Total number of sensitive audit events logged',
    ['event_type', 'sensitivity_level']
)


class MetricsCollector:
    """Helper class for collecting and updating metrics"""

    @staticmethod
    def record_audit_event(event_type: str, resource_type: str, action: str):
        """Record an audit event"""
        audit_events_total.labels(
            event_type=event_type,
            resource_type=resource_type,
            action=action
        ).inc()

    @staticmethod
    def record_audit_failed(event_type: str, error_type: str):
        """Record a failed audit event write"""
        audit_events_failed_total.labels(
            event_type=event_type,
            error_type=error_type
        ).inc()

    @staticmethod
    def record_processing_time(event_type: str, duration: float):
        """Record audit event processing duration"""
        audit_event_processing_duration.labels(event_type=event_type).observe(duration)

    @staticmethod
    def update_storage_size(size_bytes: int):
        """Update audit storage size"""
        audit_storage_size_bytes.set(size_bytes)

    @staticmethod
    def record_user_event(user_id: str, action: str):
        """Record an audit event by user"""
        audit_events_by_user.labels(
            user_id=user_id,
            action=action
        ).inc()

    @staticmethod
    def record_resource_event(resource_type: str, action: str):
        """Record an audit event by resource"""
        audit_events_by_resource.labels(
            resource_type=resource_type,
            action=action
        ).inc()

    @staticmethod
    def record_query_time(query_type: str, duration: float):
        """Record audit query duration"""
        audit_query_duration.labels(query_type=query_type).observe(duration)

    @staticmethod
    def record_retention_violation(violation_type: str):
        """Record a retention policy violation"""
        audit_retention_violations.labels(violation_type=violation_type).inc()

    @staticmethod
    def record_compliance_check(check_type: str, result: str):
        """Record a compliance check"""
        audit_compliance_checks.labels(
            check_type=check_type,
            result=result
        ).inc()

    @staticmethod
    def update_queue_size(size: int):
        """Update audit event queue size"""
        audit_event_queue_size.set(size)

    @staticmethod
    def record_batch_size(size: int):
        """Record audit batch size"""
        audit_batch_size.observe(size)

    @staticmethod
    def record_sensitive_event(event_type: str, sensitivity_level: str):
        """Record a sensitive audit event"""
        audit_sensitive_events_total.labels(
            event_type=event_type,
            sensitivity_level=sensitivity_level
        ).inc()


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
