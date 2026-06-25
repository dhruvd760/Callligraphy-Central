from typing import Optional, List, Dict
from .base_agent import BaseAgent

class AgentRegistry:
    """Localized catalog of available agents."""
    
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        """Registers an agent by its agent_name."""
        self._agents[agent.agent_name] = agent

    def get(self, name: str) -> Optional[BaseAgent]:
        """Retrieves a registered agent or safely returns None."""
        return self._agents.get(name)

    def list_agents(self) -> List[str]:
        """Returns the keys of all registered agents."""
        return list(self._agents.keys())
