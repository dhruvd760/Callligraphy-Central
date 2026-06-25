from typing import Optional, List, Dict
from .base_adk_agent import BaseADKAgent

class ADKRegistry:
    """Localized catalog of ADK-compatible agents."""
    
    def __init__(self):
        self._agents: Dict[str, BaseADKAgent] = {}

    def register(self, agent: BaseADKAgent) -> None:
        """Registers an ADK agent by its agent_name."""
        self._agents[agent.agent_name] = agent

    def get(self, name: str) -> Optional[BaseADKAgent]:
        """Retrieves a registered ADK agent or safely returns None."""
        return self._agents.get(name)

    def list_agents(self) -> List[str]:
        """Returns the keys of all registered ADK agents."""
        return list(self._agents.keys())
