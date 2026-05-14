"""
Prometheus metrics endpoint for Recurring Task Service

This module exposes Prometheus metrics for monitoring recurring task operations.
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import APIRouter, Response
import time

# Create metrics router
router = APIRouter(prefix="/metrics", tags=["metrics"])

# Metrics definitions
recurring_tasks_processed_total = Counter(
    'recurring_tasks_processed_total',
    'Total number of recurring tasks processed',
    ['task_type', 'frequency']
)

recurring_tasks_created_total = Counter(
    'recurring_tasks_created_total',
    'Total number of task instances created from recurring tasks',
    ['task_type', 'frequency']
)

recurring_tasks_failed_total = Counter(
    'recurring_tasks_failed_total',
    'Total number of failed recurring task operations',
    ['task_type', 'frequency', 'error_type']
)

recurring_task_processing_duration = Histogram(
    'recurring_task_processing_duration_seconds',
    'Time spent processing recurring tasks',
    ['task_type', 'frequency'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

active_recurring_tasks = Gauge(
    'active_recurring_tasks',
    'Current number of active recurring tasks',
    ['frequency']
)

recurring_task_next_run = Gauge(
    'recurring_task_next_run_timestamp',
    'Timestamp of next scheduled run for recurring tasks',
    ['task_id', 'frequency']
)

recurring_task_execution_lag = Histogram(
    'recurring_task_execution_lag_seconds',
    'Lag between scheduled time and actual execution',
    ['frequency'],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0]
)

recurring_task_skipped_total = Counter(
    'recurring_task_skipped_total',
    'Total number of skipped recurring task executions',
    ['task_type', 'frequency', 'reason']
)

recurring_task_success_rate = Gauge(
    'recurring_task_success_rate',
    'Success rate of recurring task executions',
    ['frequency']
)

recurring_task_queue_size = Gauge(
    'recurring_task_queue_size',
    'Current size of recurring task processing queue'
)


class MetricsCollector:
    """Helper class for collecting and updating metrics"""

    @staticmethod
    def record_task_processed(task_type: str, frequency: str):
        """Record a recurring task processed"""
        recurring_tasks_processed_total.labels(
            task_type=task_type,
            frequency=frequency
        ).inc()

    @staticmethod
    def record_task_created(task_type: str, frequency: str):
        """Record a task instance created from recurring task"""
        recurring_tasks_created_total.labels(
            task_type=task_type,
            frequency=frequency
        ).inc()

    @staticmethod
    def record_task_failed(task_type: str, frequency: str, error_type: str):
        """Record a failed recurring task operation"""
        recurring_tasks_failed_total.labels(
            task_type=task_type,
            frequency=frequency,
            error_type=error_type
        ).inc()

    @staticmethod
    def record_processing_time(task_type: str, frequency: str, duration: float):
        """Record recurring task processing duration"""
        recurring_task_processing_duration.labels(
            task_type=task_type,
            frequency=frequency
        ).observe(duration)

    @staticmethod
    def update_active_tasks(frequency: str, count: int):
        """Update active recurring tasks count"""
        active_recurring_tasks.labels(frequency=frequency).set(count)

    @staticmethod
    def update_next_run(task_id: str, frequency: str, timestamp: float):
        """Update next run timestamp for a recurring task"""
        recurring_task_next_run.labels(
            task_id=task_id,
            frequency=frequency
        ).set(timestamp)

    @staticmethod
    def record_execution_lag(frequency: str, lag_seconds: float):
        """Record execution lag for a recurring task"""
        recurring_task_execution_lag.labels(frequency=frequency).observe(lag_seconds)

    @staticmethod
    def record_task_skipped(task_type: str, frequency: str, reason: str):
        """Record a skipped recurring task execution"""
        recurring_task_skipped_total.labels(
            task_type=task_type,
            frequency=frequency,
            reason=reason
        ).inc()

    @staticmethod
    def update_success_rate(frequency: str, rate: float):
        """Update success rate for recurring tasks"""
        recurring_task_success_rate.labels(frequency=frequency).set(rate)

    @staticmethod
    def update_queue_size(size: int):
        """Update recurring task queue size"""
        recurring_task_queue_size.set(size)


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
