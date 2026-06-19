from abc import ABC, abstractmethod

class RateLimiter(ABC):
    @abstractmethod
    async def is_allowed(self, user_id: str) -> bool:
        pass