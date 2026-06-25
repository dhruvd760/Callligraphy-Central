from abc import ABC, abstractmethod

class BasePrompt(ABC):
    """Abstract base class for all prompt templates."""
    
    @property
    @abstractmethod
    def prompt_name(self) -> str:
        """Returns the unique identifier string for the prompt."""
        pass

    @abstractmethod
    def render(self, **kwargs) -> str:
        """Renders the prompt with the provided keyword arguments."""
        pass
