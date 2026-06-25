from abc import ABC, abstractmethod
from typing import Any

class BaseKnowledge(ABC):
    """Abstract base class for knowledge sources."""
    
    @property
    @abstractmethod
    def knowledge_name(self) -> str:
        """Returns the unique identifier for the knowledge source."""
        pass

    @abstractmethod
    def lookup(self, query: str) -> Any:
        """Retrieves information based on the provided query."""
        pass
