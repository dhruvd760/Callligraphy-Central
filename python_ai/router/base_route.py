from abc import ABC, abstractmethod

class BaseRoute(ABC):
    """Abstract base class for determining execution paths."""
    
    @property
    @abstractmethod
    def route_name(self) -> str:
        """Returns the unique identifier for the route."""
        pass

    @abstractmethod
    def select(self, request: str) -> str:
        """Given a request, determines which plan should execute and returns its name."""
        pass
