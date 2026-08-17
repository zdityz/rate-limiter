import time
import math
from ratekeep.algorithms.base import RateLimiterAlgorithm

class TokenBucketLimiter(RateLimiterAlgorithm):
    def __init__(self, redis_client, capacity: int, refill_rate: float):
        self.redis = redis_client
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.script = self.redis.register_script("""
            local key = KEYS[1]
            local capacity = tonumber(ARGV[1])
            local refill_rate = tonumber(ARGV[2])
            local now = tonumber(ARGV[3])
            local requested = 1
            
            local bucket = redis.call('HMGET', key, 'tokens', 'last_update')
            local tokens = tonumber(bucket[1])
            local last_update = tonumber(bucket[2])
            
            if not tokens then
                tokens = capacity
                last_update = now
            else
                local elapsed = math.max(0, now - last_update)
                local added = math.floor(elapsed * refill_rate)
                tokens = math.min(capacity, tokens + added)
                if added > 0 then
                    last_update = now
                end
            end
            
            local allowed = 0
            if tokens >= requested then
                tokens = tokens - requested
                allowed = 1
            end
            
            redis.call('HMSET', key, 'tokens', tokens, 'last_update', last_update)
            redis.call('EXPIRE', key, math.ceil(capacity / refill_rate) * 2)
            
            return allowed
        """)

    def is_allowed(self, client_id: str) -> bool:
        key = f"rate_limit:tb:{client_id}"
        now = time.time()
        result = self.script(keys=[key], args=[self.capacity, self.refill_rate, now])
        return bool(result)