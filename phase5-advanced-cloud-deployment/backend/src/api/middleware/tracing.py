"""Request tracing middleware for distributed tracing"""
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from src.lib.logging import request_id_var


class TracingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add request ID for distributed tracing

    Adds a unique request ID to each request for tracing across services.
    The request ID is propagated through:
    - Response headers (X-Request-ID)
    - Logging context
    - Downstream service calls
    """

    async def dispatch(self, request: Request, call_next):
        # Get or generate request ID
        request_id = request.headers.get('X-Request-ID')
        if not request_id:
            request_id = str(uuid.uuid4())

        # Set request ID in context for logging
        request_id_var.set(request_id)

        # Add request ID to request state
        request.state.request_id = request_id

        # Process request
        response = await call_next(request)

        # Add request ID to response headers
        response.headers['X-Request-ID'] = request_id

        return response
