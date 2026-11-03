import time
import math
from typing import Dict, List, Optional, Tuple
from fastapi import Request, HTTPException, status
import logging

logger = logging.getLogger("gaadilelo.ratelimit")

class RateLimiter:
    """
    Production-grade rate limiter.
    Supports Redis shared backend when REDIS_URL is configured,
    with an in-memory sliding-window fallback for local development and testing.
    """
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url
        self.redis_client = None
        self._memory_store: Dict[str, List[float]] = {}
        
        if redis_url:
            try:
                import redis
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                # Test ping
                self.redis_client.ping()
                logger.info(f"RateLimiter connected to Redis at {redis_url}")
            except Exception as e:
                logger.warning(f"Could not connect to Redis at {redis_url}: {e}. Falling back to in-memory store.")
                self.redis_client = None

    def _get_client_identifier(self, request: Request, key_prefix: str) -> str:
        # Check forwarded headers first for reverse proxies
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "127.0.0.1"
        return f"rl:{key_prefix}:{client_ip}"

    def check_rate_limit(self, key: str, max_requests: int, window_seconds: int) -> Tuple[bool, int]:
        """
        Returns (is_allowed, retry_after_seconds)
        """
        now = time.time()
        
        # 1. Distributed Redis backend
        if self.redis_client:
            try:
                pipe = self.redis_client.pipeline()
                current_time = now
                clear_before = current_time - window_seconds
                
                pipe.zremrangebyscore(key, 0, clear_before)
                pipe.zcard(key)
                pipe.zadd(key, {str(current_time): current_time})
                pipe.expire(key, window_seconds + 5)
                results = pipe.execute()
                
                request_count = results[1]
                if request_count >= max_requests:
                    # Fetch oldest entry in window to calculate exact retry_after
                    oldest = self.redis_client.zrange(key, 0, 0, withscores=True)
                    if oldest:
                        retry_after = max(1, math.ceil(oldest[0][1] + window_seconds - now))
                    else:
                        retry_after = window_seconds
                    return False, retry_after
                return True, 0
            except Exception as e:
                logger.error(f"Redis rate limit error: {e}. Falling back to in-memory store.")

        # 2. Local in-memory sliding window
        timestamps = self._memory_store.get(key, [])
        # Filter out timestamps older than window
        cutoff = now - window_seconds
        timestamps = [ts for ts in timestamps if ts > cutoff]
        
        if len(timestamps) >= max_requests:
            oldest_ts = timestamps[0]
            retry_after = max(1, math.ceil(oldest_ts + window_seconds - now))
            self._memory_store[key] = timestamps
            return False, retry_after

        timestamps.append(now)
        self._memory_store[key] = timestamps
        return True, 0

    def reset(self, key_prefix: Optional[str] = None):
        """Reset counters, useful for tests and administrative resets."""
        if key_prefix:
            if self.redis_client:
                keys = self.redis_client.keys(f"rl:{key_prefix}:*")
                if keys:
                    self.redis_client.delete(*keys)
            self._memory_store = {k: v for k, v in self._memory_store.items() if not k.startswith(f"rl:{key_prefix}:")}
        else:
            if self.redis_client:
                keys = self.redis_client.keys("rl:*")
                if keys:
                    self.redis_client.delete(*keys)
            self._memory_store.clear()

# Singleton instance
rate_limiter = RateLimiter()

def rate_limit(max_requests: int, window_seconds: int, key_prefix: str):
    """
    FastAPI dependency factory for rate limiting endpoints.
    """
    async def dependency(request: Request):
        identifier = rate_limiter._get_client_identifier(request, key_prefix)
        allowed, retry_after = rate_limiter.check_rate_limit(identifier, max_requests, window_seconds)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many requests for {key_prefix}. Please try again in {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)}
            )
    return dependency

