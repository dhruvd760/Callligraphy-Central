from abc import ABC, abstractmethod
from typing import Any

class BaseADKAgent(ABC):
    """Abstract interface representing a Google ADK-compatible execution contract."""
    
    @property
    @abstractmethod
    def agent_name(self) -> str:
        """Returns the unique identifier string for the agent."""
        pass

    @abstractmethod
    def run(self, request: str) -> Any:
        """Executes the agent logic following the ADK convention."""
        pass
