import time
from ratekeep.algorithms.base import RateLimiterAlgorithm

class FixedWindowLimiter(RateLimiterAlgorithm):
    def __init__(self, redis_client, limit: int, window_size: int):
        self.redis = redis_client
        self.limit = limit
        self.window_size = window_size
        self.script = self.redis.register_script("""
            local current = redis.call('GET', KEYS[1])
            if current and tonumber(current) >= tonumber(ARGV[1]) then
                return 0
            end
            current = redis.call('INCR', KEYS[1])
            if tonumber(current) == 1 then
                redis.call('EXPIRE', KEYS[1], tonumber(ARGV[2]))
            end
            return 1
        """)

    def is_allowed(self, client_id: str) -> bool:
        current_window = int(time.time() // self.window_size)
        key = f"rate_limit:fw:{client_id}:{current_window}"
        result = self.script(keys=[key], args=[self.limit, self.window_size])
        return bool(result)