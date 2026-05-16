"""Structured logging configuration for TodoBoard backend"""
import logging
import json
import sys
from datetime import datetime, timezone
from typing import Any, Dict
from contextvars import ContextVar

# Context variable for request ID
request_id_var: ContextVar[str] = ContextVar('request_id', default='')


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging

    Outputs logs in JSON format for easy parsing by log aggregation systems.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data: Dict[str, Any] = {
            'timestamp': datetime.now(timezone.utc).isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Add request ID if available
        request_id = request_id_var.get()
        if request_id:
            log_data['request_id'] = request_id

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'task_id'):
            log_data['task_id'] = record.task_id
        if hasattr(record, 'event_type'):
            log_data['event_type'] = record.event_type

        return json.dumps(log_data)


def setup_logging(level: str = "INFO") -> None:
    """
    Configure structured logging for the application

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Create JSON formatter
    formatter = JSONFormatter()

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add stdout handler with JSON formatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Set levels for third-party loggers
    logging.getLogger('uvicorn').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    logging.getLogger('dapr').setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Example usage:
# from src.lib.logging import get_logger
# logger = get_logger(__name__)
# logger.info("Task created", extra={"user_id": user_id, "task_id": task_id})
