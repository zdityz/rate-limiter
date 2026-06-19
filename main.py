from fastapi import FastAPI, HTTPException, Depends
import time
import redis.asyncio as redis
from algorithms.fixed_window import FixedWindowRateLimiter
from algorithms.sliding_window import SlidingWindowRateLimiter
from algorithms.token_bucket import TokenBucketRateLimiter
from config import config
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Rate Limiter API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

r = redis.from_url(config.redis_url, decode_responses=True)

def get_fixed_limiter():
    return FixedWindowRateLimiter(config.fixed_max_requests, config.fixed_window_seconds)

def get_sliding_limiter():
    return SlidingWindowRateLimiter(config.sliding_max_requests, config.sliding_window_seconds)

def get_token_limiter():
    return TokenBucketRateLimiter(config.token_max_tokens, config.token_refill_rate)

async def record(user_id: str, allowed: bool):
    pipe = r.pipeline()
    if allowed:
        pipe.incr("stats:total_allowed")
        pipe.incr(f"stats:user:{user_id}:allowed")
    else:
        pipe.incr("stats:total_blocked")
        pipe.incr(f"stats:user:{user_id}:blocked")
    pipe.sadd("stats:active_users", user_id)
    await pipe.execute()

@app.on_event("startup")
async def startup_event():
    start_time = await r.get("stats:start_time")
    if not start_time:
        await r.set("stats:start_time", time.time())

@app.get("/")
async def root():
    return {"message": "Rate Limiter API is running"}

@app.post("/fixed/{user_id}")
async def fixed_window(user_id: str, limiter: FixedWindowRateLimiter = Depends(get_fixed_limiter)):
    allowed = await limiter.is_allowed(user_id)
    await record(user_id, allowed)
    if allowed:
        return {"user": user_id, "algorithm": "fixed_window", "status": "allowed"}
    raise HTTPException(status_code=429, detail="Rate limit exceeded")

@app.post("/sliding/{user_id}")
async def sliding_window(user_id: str, limiter: SlidingWindowRateLimiter = Depends(get_sliding_limiter)):
    allowed = await limiter.is_allowed(user_id)
    await record(user_id, allowed)
    if allowed:
        return {"user": user_id, "algorithm": "sliding_window", "status": "allowed"}
    raise HTTPException(status_code=429, detail="Rate limit exceeded")

@app.post("/token/{user_id}")
async def token_bucket(user_id: str, limiter: TokenBucketRateLimiter = Depends(get_token_limiter)):
    allowed = await limiter.is_allowed(user_id)
    await record(user_id, allowed)
    if allowed:
        return {"user": user_id, "algorithm": "token_bucket", "status": "allowed"}
    raise HTTPException(status_code=429, detail="Rate limit exceeded")

@app.get("/stats")
async def get_stats():
    pipe = r.pipeline()
    pipe.get("stats:start_time")
    pipe.get("stats:total_allowed")
    pipe.get("stats:total_blocked")
    pipe.smembers("stats:active_users")
    results = await pipe.execute()
    
    start_time = float(results[0]) if results[0] else time.time()
    total_allowed = int(results[1] or 0)
    total_blocked = int(results[2] or 0)
    active_users = list(results[3] or [])
    
    uptime = round(time.time() - start_time, 2)
    total = total_allowed + total_blocked
    
    return {
        "uptime_seconds": uptime,
        "total_requests": total,
        "total_allowed": total_allowed,
        "total_blocked": total_blocked,
        "active_users": active_users,
        "throughput": round(total / uptime, 2) if uptime > 0 else 0
    }

@app.get("/stats/{user_id}")
async def get_user_stats(user_id: str):
    is_active = await r.sismember("stats:active_users", user_id)
    if not is_active:
        raise HTTPException(status_code=404, detail="User not found")
        
    allowed = int(await r.get(f"stats:user:{user_id}:allowed") or 0)
    blocked = int(await r.get(f"stats:user:{user_id}:blocked") or 0)
    total = allowed + blocked
    
    return {
        "user": user_id,
        "total_requests": total,
        "allowed": allowed,
        "blocked": blocked,
        "block_rate": round(blocked / total * 100, 1) if total > 0 else 0
    }