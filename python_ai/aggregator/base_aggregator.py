from abc import ABC, abstractmethod
from typing import Any

class BaseAggregator(ABC):
    """Abstract base class for aggregator components."""
    
    @property
    @abstractmethod
    def aggregator_name(self) -> str:
        """Returns the unique identifier for the aggregator."""
        pass

    @abstractmethod
    def aggregate(self, items: Any) -> Any:
        """Combines multiple items and returns an aggregated result."""
        pass
