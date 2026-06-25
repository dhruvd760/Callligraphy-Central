from abc import ABC, abstractmethod
from typing import List

class BasePlan(ABC):
    """Abstract base class for planners."""
    
    @property
    @abstractmethod
    def plan_name(self) -> str:
        """Returns the unique identifier for the plan."""
        pass

    @abstractmethod
    def build(self, request: str) -> List[str]:
        """Returns an ordered list of agent names representing the execution plan."""
        pass
