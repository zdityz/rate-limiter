import time
import pytest
from algorithms.fixed_window import FixedWindowRateLimiter
from algorithms.sliding_window import SlidingWindowRateLimiter
from algorithms.token_bucket import TokenBucketRateLimiter


# ── Fixed Window ──────────────────────────────────────────────
class TestFixedWindow:
    def test_allows_requests_within_limit(self):
        limiter = FixedWindowRateLimiter(max_requests=3, window_seconds=10)
        assert limiter.is_allowed("user1") == True
        assert limiter.is_allowed("user1") == True
        assert limiter.is_allowed("user1") == True

    def test_blocks_requests_over_limit(self):
        limiter = FixedWindowRateLimiter(max_requests=3, window_seconds=10)
        for _ in range(3):
            limiter.is_allowed("user1")
        assert limiter.is_allowed("user1") == False

    def test_resets_after_window(self):
        limiter = FixedWindowRateLimiter(max_requests=3, window_seconds=1)
        for _ in range(3):
            limiter.is_allowed("user1")
        time.sleep(1.1)
        assert limiter.is_allowed("user1") == True

    def test_different_users_are_independent(self):
        limiter = FixedWindowRateLimiter(max_requests=2, window_seconds=10)
        for _ in range(2):
            limiter.is_allowed("alice")
        assert limiter.is_allowed("alice") == False
        assert limiter.is_allowed("bob") == True


# ── Sliding Window ────────────────────────────────────────────
class TestSlidingWindow:
    def test_allows_requests_within_limit(self):
        limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=10)
        assert limiter.is_allowed("user1") == True
        assert limiter.is_allowed("user1") == True
        assert limiter.is_allowed("user1") == True

    def test_blocks_requests_over_limit(self):
        limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=10)
        for _ in range(3):
            limiter.is_allowed("user1")
        assert limiter.is_allowed("user1") == False

    def test_resets_after_window(self):
        limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=1)
        for _ in range(3):
            limiter.is_allowed("user1")
        time.sleep(1.1)
        assert limiter.is_allowed("user1") == True

    def test_different_users_are_independent(self):
        limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=10)
        for _ in range(2):
            limiter.is_allowed("alice")
        assert limiter.is_allowed("alice") == False
        assert limiter.is_allowed("bob") == True


# ── Token Bucket ──────────────────────────────────────────────
class TestTokenBucket:
    def test_allows_requests_within_limit(self):
        limiter = TokenBucketRateLimiter(max_tokens=3, refill_rate=1)
        assert limiter.is_allowed("user1") == True
        assert limiter.is_allowed("user1") == True
        assert limiter.is_allowed("user1") == True

    def test_blocks_when_bucket_empty(self):
        limiter = TokenBucketRateLimiter(max_tokens=3, refill_rate=1)
        for _ in range(3):
            limiter.is_allowed("user1")
        assert limiter.is_allowed("user1") == False

    def test_refills_over_time(self):
        limiter = TokenBucketRateLimiter(max_tokens=3, refill_rate=2)
        for _ in range(3):
            limiter.is_allowed("user1")
        time.sleep(1.1)
        assert limiter.is_allowed("user1") == True

    def test_different_users_are_independent(self):
        limiter = TokenBucketRateLimiter(max_tokens=2, refill_rate=1)
        for _ in range(2):
            limiter.is_allowed("alice")
        assert limiter.is_allowed("alice") == False
        assert limiter.is_allowed("bob") == True