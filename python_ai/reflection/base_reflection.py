from abc import ABC, abstractmethod
from typing import Any

class BaseReflection(ABC):
    """Abstract base class for reflection sources."""
    
    @property
    @abstractmethod
    def reflection_name(self) -> str:
        """Returns the unique identifier for the reflection block."""
        pass

    @abstractmethod
    def analyze(self, input_data: Any) -> Any:
        """Analyzes input data and returns a structured reflection."""
        pass
