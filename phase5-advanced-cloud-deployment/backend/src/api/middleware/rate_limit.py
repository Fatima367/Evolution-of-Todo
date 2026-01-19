"""Rate limiting middleware for API endpoints"""
import time
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import asyncio
from threading import Lock


class TokenBucket:
    """Token bucket algorithm for rate limiting"""

    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize token bucket

        Args:
            capacity: Maximum number of tokens (requests)
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
        self.lock = Lock()

    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens from the bucket

        Args:
            tokens: Number of tokens to consume

        Returns:
            True if tokens were consumed, False if rate limit exceeded
        """
        with self.lock:
            now = time.time()
            # Refill tokens based on time elapsed
            elapsed = now - self.last_refill
            self.tokens = min(
                self.capacity,
                self.tokens + elapsed * self.refill_rate
            )
            self.last_refill = now

            # Try to consume tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using token bucket algorithm

    Limits requests per user to prevent abuse:
    - 100 requests per minute per authenticated user
    - 20 requests per minute per IP for unauthenticated requests

    Uses in-memory storage for simplicity. For production with multiple
    instances, consider using Redis with slowapi library.
    """

    def __init__(self, app, requests_per_minute: int = 100,
                 anonymous_requests_per_minute: int = 20):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.anonymous_requests_per_minute = anonymous_requests_per_minute

        # Storage for token buckets per user/IP
        self.buckets: Dict[str, TokenBucket] = {}
        self.cleanup_interval = 300  # Cleanup every 5 minutes
        self.last_cleanup = time.time()

    def _get_identifier(self, request: Request) -> Tuple[str, int]:
        """
        Get identifier for rate limiting (user_id or IP)

        Returns:
            Tuple of (identifier, rate_limit)
        """
        # Try to get user_id from request state (set by auth middleware)
        user_id = getattr(request.state, 'user_id', None)

        if user_id:
            return f"user:{user_id}", self.requests_per_minute

        # Fall back to IP address for unauthenticated requests
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}", self.anonymous_requests_per_minute

    def _get_or_create_bucket(self, identifier: str, rate_limit: int) -> TokenBucket:
        """Get existing bucket or create new one"""
        if identifier not in self.buckets:
            # Convert requests per minute to tokens per second
            refill_rate = rate_limit / 60.0
            self.buckets[identifier] = TokenBucket(
                capacity=rate_limit,
                refill_rate=refill_rate
            )
        return self.buckets[identifier]

    def _cleanup_old_buckets(self):
        """Remove inactive buckets to prevent memory leak"""
        now = time.time()
        if now - self.last_cleanup < self.cleanup_interval:
            return

        # Remove buckets that haven't been used in 10 minutes
        inactive_threshold = now - 600
        to_remove = [
            key for key, bucket in self.buckets.items()
            if bucket.last_refill < inactive_threshold
        ]

        for key in to_remove:
            del self.buckets[key]

        self.last_cleanup = now

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""
        # Skip rate limiting for health check endpoints
        if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
            return await call_next(request)

        # Get identifier and rate limit
        identifier, rate_limit = self._get_identifier(request)

        # Get or create token bucket
        bucket = self._get_or_create_bucket(identifier, rate_limit)

        # Try to consume a token
        if not bucket.consume():
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit: {rate_limit} requests per minute",
                    "retry_after": 60  # Retry after 60 seconds
                },
                headers={"Retry-After": "60"}
            )

        # Cleanup old buckets periodically
        self._cleanup_old_buckets()

        # Add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(int(bucket.tokens))

        return response
