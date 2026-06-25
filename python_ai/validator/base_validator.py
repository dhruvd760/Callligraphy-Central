from abc import ABC, abstractmethod
from typing import Any

class BaseValidator(ABC):
    """Abstract base class for validator components."""
    
    @property
    @abstractmethod
    def validator_name(self) -> str:
        """Returns the unique identifier for the validator."""
        pass

    @abstractmethod
    def validate(self, candidate: Any) -> Any:
        """Validates a candidate output and returns a structured validation result."""
        pass
