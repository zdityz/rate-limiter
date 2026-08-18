from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import Match
from ratekeep.adaptive.analyzer import AdaptiveAnalyzer
from ratekeep.observability.metrics import MetricsCollector

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_client, limiter_class, adaptive: bool = False):
        super().__init__(app)
        self.redis = redis_client
        self.limiter_class = limiter_class
        self.adaptive = adaptive
        self.analyzer = AdaptiveAnalyzer(redis_client) if adaptive else None
        self.metrics = MetricsCollector(redis_client)

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
            effective_limit = route_limit
            
            if self.adaptive:
                effective_limit = self.analyzer.analyze_and_adjust(client_id, route_limit)

            window_seconds = self._parse_window(route_window)
            limiter = self.limiter_class(self.redis, effective_limit, window_seconds)
            
            is_allowed = limiter.is_allowed(client_id)
            self.metrics.record_request(client_id, is_allowed)
            
            if not is_allowed:
                raise HTTPException(status_code=429, detail="Too Many Requests")
                
        return await call_next(request)

    def _parse_window(self, window: str) -> int:
        unit = window[-1]
        value = int(window[:-1])
        if unit == 's': return value
        if unit == 'm': return value * 60
        if unit == 'h': return value * 3600
        return value