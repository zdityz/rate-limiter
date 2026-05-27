import time
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

class SlidingWindowRateLimiter:
    def __init__(self, max_requests, window_seconds):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def is_allowed(self, user_id):
        key = f"sliding:{user_id}"
        now = time.time()
        window_start = now - self.window_seconds

        pipe = r.pipeline()
        # Remove timestamps outside the window
        pipe.zremrangebyscore(key, 0, window_start)
        # Count requests in current window
        pipe.zcard(key)
        # Add current request timestamp
        pipe.zadd(key, {str(now): now})
        # Set expiry so Redis cleans up old keys
        pipe.expire(key, self.window_seconds)
        results = pipe.execute()

        request_count = results[1]
        return request_count < self.max_requests