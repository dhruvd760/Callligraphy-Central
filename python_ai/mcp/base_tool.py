from abc import ABC, abstractmethod
from typing import Any

class BaseMCPTool(ABC):
    """Abstract base class for MCP tool components."""
    
    def __init__(self, orchestrator: Any = None):
        self.orchestrator = orchestrator
        
    @property
    @abstractmethod
    def tool_name(self) -> str:
        """Returns the unique identifier for the MCP tool."""
        pass

    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        """Executes the tool with the provided arguments."""
        pass
