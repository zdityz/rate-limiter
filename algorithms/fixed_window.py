import time
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

class FixedWindowRateLimiter:
    def __init__(self, max_requests, window_seconds):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def is_allowed(self, user_id):
        key = f"fixed:{user_id}"
        current = r.get(key)

        if current is None:
            # First request — set count to 1 with expiry
            r.set(key, 1, ex=self.window_seconds)
            return True

        if int(current) < self.max_requests:
            r.incr(key)
            return True

        return False