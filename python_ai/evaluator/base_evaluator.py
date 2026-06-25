from abc import ABC, abstractmethod
from typing import Any

class BaseEvaluator(ABC):
    """Abstract base class for evaluator components."""
    
    @property
    @abstractmethod
    def evaluator_name(self) -> str:
        """Returns the unique identifier for the evaluator."""
        pass

    @abstractmethod
    def evaluate(self, candidate: Any) -> Any:
        """Evaluates a candidate and returns structured assessment."""
        pass
