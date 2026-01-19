"""Caching service for frequently accessed data"""
import json
import hashlib
from typing import Any, Optional, Callable
from datetime import timedelta
from functools import wraps
import os

# Try to import Redis, fall back to in-memory cache if not available
try:
    import redis
    from redis.exceptions import RedisError
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from src.lib.logging import get_logger

logger = get_logger(__name__)


class InMemoryCache:
    """Simple in-memory cache implementation for development/testing"""

    def __init__(self):
        self._cache = {}
        self._expiry = {}

    def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        import time
        if key in self._cache:
            # Check if expired
            if key in self._expiry and time.time() > self._expiry[key]:
                del self._cache[key]
                del self._expiry[key]
                return None
            return self._cache[key]
        return None

    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """Set value in cache with optional expiry"""
        import time
        self._cache[key] = value
        if ex:
            self._expiry[key] = time.time() + ex
        return True

    def delete(self, key: str) -> int:
        """Delete key from cache"""
        if key in self._cache:
            del self._cache[key]
            if key in self._expiry:
                del self._expiry[key]
            return 1
        return 0

    def flushdb(self):
        """Clear all cache"""
        self._cache.clear()
        self._expiry.clear()


class CacheService:
    """
    Caching service for frequently accessed data

    Supports Redis for production and in-memory cache for development.
    Provides TTL-based caching with automatic serialization.
    """

    def __init__(self):
        """Initialize cache service"""
        self.redis_url = os.getenv("REDIS_URL")
        self.use_redis = REDIS_AVAILABLE and self.redis_url

        if self.use_redis:
            try:
                self.client = redis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
                # Test connection
                self.client.ping()
                logger.info("Redis cache initialized successfully")
            except (RedisError, Exception) as e:
                logger.warning(f"Failed to connect to Redis, falling back to in-memory cache: {e}")
                self.use_redis = False
                self.client = InMemoryCache()
        else:
            logger.info("Using in-memory cache (Redis not available)")
            self.client = InMemoryCache()

    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Generate cache key from prefix and arguments

        Args:
            prefix: Key prefix (e.g., 'user', 'task', 'tags')
            *args: Positional arguments to include in key
            **kwargs: Keyword arguments to include in key

        Returns:
            Cache key string
        """
        # Combine all arguments into a string
        key_parts = [str(arg) for arg in args]
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        key_str = ":".join(key_parts)

        # Hash if too long
        if len(key_str) > 100:
            key_hash = hashlib.md5(key_str.encode()).hexdigest()
            return f"{prefix}:{key_hash}"

        return f"{prefix}:{key_str}" if key_str else prefix

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        try:
            value = self.client.get(key)
            if value:
                # Deserialize JSON
                return json.loads(value)
            return None
        except (RedisError, json.JSONDecodeError, Exception) as e:
            logger.warning(f"Cache get error for key {key}: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """
        Set value in cache with TTL

        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Time to live in seconds (default: 5 minutes)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Serialize to JSON
            serialized = json.dumps(value)
            self.client.set(key, serialized, ex=ttl)
            return True
        except (RedisError, TypeError, Exception) as e:
            logger.warning(f"Cache set error for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete key from cache

        Args:
            key: Cache key

        Returns:
            True if key was deleted, False otherwise
        """
        try:
            result = self.client.delete(key)
            return result > 0
        except (RedisError, Exception) as e:
            logger.warning(f"Cache delete error for key {key}: {e}")
            return False

    def clear(self) -> bool:
        """
        Clear all cache entries

        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.flushdb()
            return True
        except (RedisError, Exception) as e:
            logger.error(f"Cache clear error: {e}")
            return False

    def get_user_preferences(self, user_id: str) -> Optional[dict]:
        """Get cached user preferences"""
        key = self._make_key("user_prefs", user_id)
        return self.get(key)

    def set_user_preferences(self, user_id: str, preferences: dict, ttl: int = 3600) -> bool:
        """Cache user preferences (1 hour TTL)"""
        key = self._make_key("user_prefs", user_id)
        return self.set(key, preferences, ttl)

    def get_user_tags(self, user_id: str) -> Optional[list]:
        """Get cached user tags"""
        key = self._make_key("user_tags", user_id)
        return self.get(key)

    def set_user_tags(self, user_id: str, tags: list, ttl: int = 600) -> bool:
        """Cache user tags (10 minutes TTL)"""
        key = self._make_key("user_tags", user_id)
        return self.set(key, tags, ttl)

    def invalidate_user_cache(self, user_id: str) -> bool:
        """Invalidate all cache entries for a user"""
        try:
            # Delete user-specific cache keys
            keys_to_delete = [
                self._make_key("user_prefs", user_id),
                self._make_key("user_tags", user_id),
            ]
            for key in keys_to_delete:
                self.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error invalidating user cache: {e}")
            return False


# Global cache service instance
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """
    Get or create global cache service instance

    Returns:
        CacheService instance
    """
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service


def cached(prefix: str, ttl: int = 300):
    """
    Decorator for caching function results

    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds

    Example:
        @cached("task_stats", ttl=600)
        def get_task_statistics(user_id: str):
            # Expensive computation
            return stats
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache_service()

            # Generate cache key from function arguments
            key = cache._make_key(prefix, *args, **kwargs)

            # Try to get from cache
            cached_value = cache.get(key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {key}")
                return cached_value

            # Cache miss - call function
            logger.debug(f"Cache miss for {key}")
            result = func(*args, **kwargs)

            # Store in cache
            cache.set(key, result, ttl)

            return result

        return wrapper
    return decorator
