from abc import ABC, abstractmethod
from typing import Any

class BaseSelector(ABC):
    """Abstract base class for selector components."""
    
    @property
    @abstractmethod
    def selector_name(self) -> str:
        """Returns the unique identifier for the selector."""
        pass

    @abstractmethod
    def select(self, candidates: Any) -> Any:
        """Selects the best candidate and returns the choice with assessment."""
        pass
