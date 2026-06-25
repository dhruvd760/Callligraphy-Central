from abc import ABC, abstractmethod
from typing import Any

class BaseMemoryStore(ABC):
    """Abstract base class for memory store components."""
    
    @property
    @abstractmethod
    def memory_store_name(self) -> str:
        """Returns the unique identifier for the memory store."""
        pass

    @abstractmethod
    def save(self, key: str, value: Any) -> None:
        """Saves a value to the memory store under the specified key."""
        pass

    @abstractmethod
    def load(self, key: str) -> Any:
        """Loads a value from the memory store by its key."""
        pass
