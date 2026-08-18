from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import redis
from config import config
from ratekeep import limit, RateLimitMiddleware
from ratekeep.observability.metrics import MetricsCollector
from ratekeep.algorithms.fixed_window import FixedWindowLimiter

app = FastAPI(title="Rate Limiter API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis_client = redis.from_url(config.redis_url)

app.add_middleware(
    RateLimitMiddleware,
    redis_client=redis_client,
    limiter_class=FixedWindowLimiter,
    adaptive=True
)

@app.get("/")
def root():
    return {"message": "Rate Limiter API is running"}

@app.get("/metrics")
def get_metrics():
    collector = MetricsCollector(redis_client)
    return Response(content=collector.export_prometheus(), media_type="text/plain")

@app.post("/fixed/{user_id}")
@limit(requests=10, window="60s")
def fixed_window(user_id: str):
    return {"user": user_id, "algorithm": "fixed_window", "status": "allowed"}

@app.post("/sliding/{user_id}")
@limit(requests=10, window="60s")
def sliding_window(user_id: str):
    return {"user": user_id, "algorithm": "sliding_window", "status": "allowed"}

@app.post("/token/{user_id}")
@limit(requests=10, window="60s")
def token_bucket(user_id: str):
    return {"user": user_id, "algorithm": "token_bucket", "status": "allowed"}