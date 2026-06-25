from typing import Optional, Any
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.agent_registry import AgentRegistry
from memory.context_manager import ContextManager
from .base_adk_agent import BaseADKAgent

class _ADKWrapper(BaseADKAgent):
    """Internal wrapper that bridges a BaseAgent into a BaseADKAgent."""
    def __init__(self, base_agent):
        self._base_agent = base_agent

    @property
    def agent_name(self) -> str:
        return self._base_agent.agent_name

    def run(self, request: str) -> Any:
        return self._base_agent.process(request)

class ADKAdapter:
    """
    Adapter bridging our existing BaseAgent framework into ADK-style agents.
    """
    def __init__(self, agent_registry: AgentRegistry, context_manager: ContextManager):
        self.agent_registry = agent_registry
        self.context_manager = context_manager

    def adapt(self, agent_name: str) -> Optional[BaseADKAgent]:
        """
        Dynamically wraps an existing BaseAgent as an ADK compatible agent.
        Safely returns None if the BaseAgent is missing.
        """
        base_agent = self.agent_registry.get(agent_name)
        if base_agent is None:
            return None
        return _ADKWrapper(base_agent)
