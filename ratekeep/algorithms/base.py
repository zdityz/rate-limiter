from abc import ABC, abstractmethod

class RateLimiterAlgorithm(ABC):
    
    @abstractmethod
    def is_allowed(self, client_id: str) -> bool:
        pass