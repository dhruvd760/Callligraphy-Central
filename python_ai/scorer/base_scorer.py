from abc import ABC, abstractmethod
from typing import Any

class BaseScorer(ABC):
    """Abstract base class for scorer components."""
    
    @property
    @abstractmethod
    def scorer_name(self) -> str:
        """Returns the unique identifier for the scorer."""
        pass

    @abstractmethod
    def score(self, candidate: Any) -> Any:
        """Scores a candidate and returns structured assessment."""
        pass
