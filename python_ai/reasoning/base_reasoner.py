from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseReasoner(ABC):
    """Abstract base class for context reasoners."""
    
    @property
    @abstractmethod
    def reasoner_name(self) -> str:
        """Returns the unique identifier for the reasoner."""
        pass

    @abstractmethod
    def reason(self, request: str, memory_context: Any) -> Dict[str, Any]:
        """Given a request and context, returns structured reasoning output."""
        pass
