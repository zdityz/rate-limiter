from pydantic_settings import BaseSettings

class RateLimitConfig(BaseSettings):
    fixed_max_requests: int = 5
    fixed_window_seconds: int = 10
    
    sliding_max_requests: int = 5
    sliding_window_seconds: int = 10
    
    token_max_tokens: int = 5
    token_refill_rate: int = 1
    
    redis_url: str = "redis://localhost:6379/0"

config = RateLimitConfig()