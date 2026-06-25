from abc import ABC, abstractmethod
from typing import Any

class BaseRanker(ABC):
    """Abstract base class for ranker components."""
    
    @property
    @abstractmethod
    def ranker_name(self) -> str:
        """Returns the unique identifier for the ranker."""
        pass

    @abstractmethod
    def rank(self, candidates: Any) -> Any:
        """Ranks candidates and returns the best one with assessment."""
        pass
