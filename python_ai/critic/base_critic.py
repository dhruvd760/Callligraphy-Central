from abc import ABC, abstractmethod
from typing import Any

class BaseCritic(ABC):
    """Abstract base class for critic components."""
    
    @property
    @abstractmethod
    def critic_name(self) -> str:
        """Returns the unique identifier for the critic."""
        pass

    @abstractmethod
    def evaluate(self, candidate: Any) -> Any:
        """Evaluates a candidate output and returns a critique."""
        pass
