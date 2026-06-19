import redis.asyncio as redis
from config import config
from algorithms.base import RateLimiter

r = redis.from_url(config.redis_url, decode_responses=True)

class FixedWindowRateLimiter(RateLimiter):
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def is_allowed(self, user_id: str) -> bool:
        key = f"fixed:{user_id}"
        current = await r.get(key)

        if current is None:
            await r.set(key, 1, ex=self.window_seconds)
            return True

        if int(current) < self.max_requests:
            await r.incr(key)
            return True

        return False