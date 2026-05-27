from fastapi import FastAPI, HTTPException
from algorithms.fixed_window import FixedWindowRateLimiter
from algorithms.sliding_window import SlidingWindowRateLimiter
from algorithms.token_bucket import TokenBucketRateLimiter
from config import FIXED_WINDOW, SLIDING_WINDOW, TOKEN_BUCKET
import time
import threading

app = FastAPI(title="Rate Limiter API")

# Instances using config values
fixed = FixedWindowRateLimiter(**FIXED_WINDOW)
sliding = SlidingWindowRateLimiter(**SLIDING_WINDOW)
token = TokenBucketRateLimiter(**TOKEN_BUCKET)

# Monitoring data
stats_lock = threading.Lock()
stats = {
    "total_allowed": 0,
    "total_blocked": 0,
    "start_time": time.time(),
    "users": {}   # per-user breakdown
}

def record(user_id, allowed):
    with stats_lock:
        # Global counts
        if allowed:
            stats["total_allowed"] += 1
        else:
            stats["total_blocked"] += 1

        # Per-user counts
        if user_id not in stats["users"]:
            stats["users"][user_id] = {"allowed": 0, "blocked": 0}
        if allowed:
            stats["users"][user_id]["allowed"] += 1
        else:
            stats["users"][user_id]["blocked"] += 1

@app.get("/")
def root():
    return {"message": "Rate Limiter API is running"}

@app.post("/fixed/{user_id}")
def fixed_window(user_id: str):
    allowed = fixed.is_allowed(user_id)
    record(user_id, allowed)
    if allowed:
        return {"user": user_id, "algorithm": "fixed_window", "status": "allowed"}
    raise HTTPException(status_code=429, detail="Rate limit exceeded")

@app.post("/sliding/{user_id}")
def sliding_window(user_id: str):
    allowed = sliding.is_allowed(user_id)
    record(user_id, allowed)
    if allowed:
        return {"user": user_id, "algorithm": "sliding_window", "status": "allowed"}
    raise HTTPException(status_code=429, detail="Rate limit exceeded")

@app.post("/token/{user_id}")
def token_bucket(user_id: str):
    allowed = token.is_allowed(user_id)
    record(user_id, allowed)
    if allowed:
        return {"user": user_id, "algorithm": "token_bucket", "status": "allowed"}
    raise HTTPException(status_code=429, detail="Rate limit exceeded")

@app.get("/stats")
def get_stats():
    with stats_lock:
        uptime = round(time.time() - stats["start_time"], 2)
        total = stats["total_allowed"] + stats["total_blocked"]
        return {
            "uptime_seconds": uptime,
            "total_requests": total,
            "total_allowed": stats["total_allowed"],
            "total_blocked": stats["total_blocked"],
            "active_users": list(stats["users"].keys()),
            "throughput": round(total / uptime, 2) if uptime > 0 else 0
        }

@app.get("/stats/{user_id}")
def get_user_stats(user_id: str):
    with stats_lock:
        if user_id not in stats["users"]:
            raise HTTPException(status_code=404, detail="User not found")
        user_data = stats["users"][user_id]
        total = user_data["allowed"] + user_data["blocked"]
        return {
            "user": user_id,
            "total_requests": total,
            "allowed": user_data["allowed"],
            "blocked": user_data["blocked"],
            "block_rate": round(user_data["blocked"] / total * 100, 1) if total > 0 else 0
        }