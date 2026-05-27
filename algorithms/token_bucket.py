import time
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

class TokenBucketRateLimiter:
    def __init__(self, max_tokens, refill_rate):
        self.max_tokens = max_tokens
        self.refill_rate = refill_rate

    def is_allowed(self, user_id):
        tokens_key = f"token:tokens:{user_id}"
        time_key = f"token:time:{user_id}"

        now = time.time()

        tokens = r.get(tokens_key)
        last_refill = r.get(time_key)

        if tokens is None:
            # New user — full bucket
            r.set(tokens_key, self.max_tokens - 1)
            r.set(time_key, now)
            return True

        tokens = float(tokens)
        last_refill = float(last_refill)

        # Refill tokens based on elapsed time
        elapsed = now - last_refill
        tokens = min(self.max_tokens, tokens + elapsed * self.refill_rate)

        if tokens >= 1:
            r.set(tokens_key, tokens - 1)
            r.set(time_key, now)
            return True

        return False