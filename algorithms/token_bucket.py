import time
import redis.asyncio as redis
from config import config
from algorithms.base import RateLimiter

r = redis.from_url(config.redis_url, decode_responses=True)

class TokenBucketRateLimiter(RateLimiter):
    def __init__(self, max_tokens: int, refill_rate: int):
        self.max_tokens = max_tokens
        self.refill_rate = refill_rate

    async def is_allowed(self, user_id: str) -> bool:
        tokens_key = f"token:tokens:{user_id}"
        time_key = f"token:time:{user_id}"

        now = time.time()

        tokens = await r.get(tokens_key)
        last_refill = await r.get(time_key)

        if tokens is None:
            await r.set(tokens_key, self.max_tokens - 1)
            await r.set(time_key, now)
            return True

        tokens = float(tokens)
        last_refill = float(last_refill)

        elapsed = now - last_refill
        tokens = min(self.max_tokens, tokens + elapsed * self.refill_rate)

        if tokens >= 1:
            await r.set(tokens_key, tokens - 1)
            await r.set(time_key, now)
            return True

        return False