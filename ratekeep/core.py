import functools
from typing import Callable, Any

def limit(requests: int, window: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)
        
        setattr(wrapper, "_rate_limit_requests", requests)
        setattr(wrapper, "_rate_limit_window", window)
        return wrapper
    return decorator