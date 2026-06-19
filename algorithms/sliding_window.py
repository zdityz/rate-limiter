import time
import redis.asyncio as redis
from config import config
from algorithms.base import RateLimiter

r = redis.from_url(config.redis_url, decode_responses=True)

class SlidingWindowRateLimiter(RateLimiter):
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def is_allowed(self, user_id: str) -> bool:
        key = f"sliding:{user_id}"
        now = time.time()
        window_start = now - self.window_seconds

        pipe = r.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zcard(key)
        pipe.zadd(key, {str(now): now})
        pipe.expire(key, self.window_seconds)
        results = await pipe.execute()

        request_count = results[1]
        return request_count < self.max_requests