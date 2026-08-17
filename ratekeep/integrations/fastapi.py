from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import Match

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_client, limiter_class):
        super().__init__(app)
        self.redis = redis_client
        self.limiter_class = limiter_class

    async def dispatch(self, request: Request, call_next):
        client_id = request.client.host
        route_limit, route_window = None, None
        
        for route in request.app.routes:
            match, _ = route.matches(request.scope)
            if match == Match.FULL:
                endpoint = getattr(route, "endpoint", None)
                if endpoint:
                    route_limit = getattr(endpoint, "_rate_limit_requests", None)
                    route_window = getattr(endpoint, "_rate_limit_window", None)
                break

        if route_limit and route_window:
            window_seconds = self._parse_window(route_window)
            limiter = self.limiter_class(self.redis, route_limit, window_seconds)
            
            if not limiter.is_allowed(client_id):
                raise HTTPException(status_code=429, detail="Too Many Requests")
                
        return await call_next(request)

    def _parse_window(self, window: str) -> int:
        unit = window[-1]
        value = int(window[:-1])
        if unit == 's': return value
        if unit == 'm': return value * 60
        if unit == 'h': return value * 3600
        return value