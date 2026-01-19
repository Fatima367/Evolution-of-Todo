"""Request/response logging middleware"""
import time
import json
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import Message
from src.lib.logging import get_logger, request_id_var

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for comprehensive request/response logging

    Logs:
    - Request method, path, headers, query parameters
    - Response status code, duration
    - User ID (if authenticated)
    - Request ID (correlation ID)
    - Request/response body (configurable)
    """

    def __init__(self, app, log_request_body: bool = False, log_response_body: bool = False):
        """
        Initialize logging middleware

        Args:
            app: FastAPI application
            log_request_body: Whether to log request body (default: False for security)
            log_response_body: Whether to log response body (default: False for performance)
        """
        super().__init__(app)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with logging"""
        start_time = time.time()

        # Get request ID from context (set by tracing middleware)
        request_id = request_id_var.get() or getattr(request.state, 'request_id', 'unknown')

        # Get user ID if authenticated
        user_id = getattr(request.state, 'user_id', None)

        # Log incoming request
        request_log = {
            'event': 'request_started',
            'method': request.method,
            'path': request.url.path,
            'query_params': dict(request.query_params),
            'client_ip': request.client.host if request.client else None,
            'user_agent': request.headers.get('user-agent'),
            'request_id': request_id,
        }

        if user_id:
            request_log['user_id'] = user_id

        # Optionally log request body (be careful with sensitive data)
        if self.log_request_body and request.method in ['POST', 'PUT', 'PATCH']:
            try:
                body = await request.body()
                if body:
                    # Try to parse as JSON
                    try:
                        request_log['request_body'] = json.loads(body.decode())
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        request_log['request_body'] = '<binary or invalid JSON>'

                    # Important: Set body back for route handlers to read
                    async def receive() -> Message:
                        return {"type": "http.request", "body": body}
                    request._receive = receive
            except Exception as e:
                logger.warning(f"Failed to read request body: {e}")

        logger.info("Incoming request", extra=request_log)

        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log exception
            duration = time.time() - start_time
            error_log = {
                'event': 'request_failed',
                'method': request.method,
                'path': request.url.path,
                'duration_ms': round(duration * 1000, 2),
                'error': str(e),
                'error_type': type(e).__name__,
                'request_id': request_id,
            }
            if user_id:
                error_log['user_id'] = user_id

            logger.error("Request failed with exception", extra=error_log, exc_info=True)
            raise

        # Calculate duration
        duration = time.time() - start_time

        # Log response
        response_log = {
            'event': 'request_completed',
            'method': request.method,
            'path': request.url.path,
            'status_code': response.status_code,
            'duration_ms': round(duration * 1000, 2),
            'request_id': request_id,
        }

        if user_id:
            response_log['user_id'] = user_id

        # Optionally log response body (not recommended for large responses)
        if self.log_response_body:
            # Note: This requires buffering the response which can impact performance
            response_log['response_body'] = '<body logging not implemented for streaming responses>'

        # Log at appropriate level based on status code
        if response.status_code >= 500:
            logger.error("Request completed with server error", extra=response_log)
        elif response.status_code >= 400:
            logger.warning("Request completed with client error", extra=response_log)
        else:
            logger.info("Request completed successfully", extra=response_log)

        # Add duration header to response
        response.headers['X-Response-Time'] = f"{round(duration * 1000, 2)}ms"

        return response


class SensitiveDataFilter:
    """
    Filter to redact sensitive data from logs

    Use this to prevent logging passwords, tokens, API keys, etc.
    """

    SENSITIVE_FIELDS = {
        'password', 'token', 'secret', 'api_key', 'apikey',
        'authorization', 'auth', 'jwt', 'bearer', 'credit_card',
        'ssn', 'social_security'
    }

    @classmethod
    def filter_dict(cls, data: dict) -> dict:
        """
        Recursively filter sensitive fields from dictionary

        Args:
            data: Dictionary to filter

        Returns:
            Filtered dictionary with sensitive values redacted
        """
        if not isinstance(data, dict):
            return data

        filtered = {}
        for key, value in data.items():
            # Check if key is sensitive
            if any(sensitive in key.lower() for sensitive in cls.SENSITIVE_FIELDS):
                filtered[key] = '***REDACTED***'
            elif isinstance(value, dict):
                filtered[key] = cls.filter_dict(value)
            elif isinstance(value, list):
                filtered[key] = [
                    cls.filter_dict(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                filtered[key] = value

        return filtered
