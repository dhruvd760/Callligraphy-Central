from abc import ABC, abstractmethod
from typing import Optional, Any
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from memory.context_manager import ContextManager

class BaseAgent(ABC):
    """
    Lightweight abstract base class defining the contract for all specialized agents.
    """
    def __init__(self, context_manager: Optional[ContextManager] = None):
        self.context_manager = context_manager

    @property
    @abstractmethod
    def agent_name(self) -> str:
        """Returns the string identifier of the agent."""
        pass

    @abstractmethod
    def process(self, request: str) -> Any:
        """
        Contains the core agent execution logic.
        Returns Any to preserve flexibility for future agent types and ADK integrations.
        """
        pass

    def parse_request(self, request: str) -> dict:
        """Parses a JSON request and securely validates it is a dictionary."""
        import json
        parsed = json.loads(request)
        if not isinstance(parsed, dict):
            raise ValueError("Invalid request format. Expected JSON dictionary.")
        return parsed
