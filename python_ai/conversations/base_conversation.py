from abc import ABC, abstractmethod
from typing import Any

class BaseConversation(ABC):
    """Abstract base class for conversations."""
    
    @property
    @abstractmethod
    def conversation_name(self) -> str:
        """Returns the unique identifier for the conversation."""
        pass

    @abstractmethod
    def respond(self, message: str, history: list) -> Any:
        """Generates a response using prior history."""
        pass
