from abc import ABC, abstractmethod
from typing import Any

class BaseTool(ABC):
    """Abstract base class for all tools."""
    
    @property
    @abstractmethod
    def tool_name(self) -> str:
        """Returns the unique identifier string for the tool."""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Executes the tool's core logic with the provided arguments."""
        pass
