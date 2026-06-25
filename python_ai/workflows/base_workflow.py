from abc import ABC, abstractmethod
from typing import Any

class BaseWorkflow(ABC):
    """Abstract base class for workflows."""
    
    @property
    @abstractmethod
    def workflow_name(self) -> str:
        """Returns the unique identifier for the workflow."""
        pass

    @abstractmethod
    def execute(self, request: str) -> Any:
        """Executes the workflow logic using the provided request."""
        pass
