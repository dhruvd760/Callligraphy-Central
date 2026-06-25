from typing import Dict, Optional, List
from .base_critic import BaseCritic

class CriticRegistry:
    """Localized catalog of available critic models."""
    
    def __init__(self):
        self._critics: Dict[str, BaseCritic] = {}

    def register(self, critic: BaseCritic) -> None:
        """Registers a critic by its critic_name."""
        self._critics[critic.critic_name] = critic

    def get(self, name: str) -> Optional[BaseCritic]:
        """Retrieves a registered critic safely returning None if missing."""
        return self._critics.get(name)

    def list_critics(self) -> List[str]:
        """Returns the keys of all registered critic blocks."""
        return list(self._critics.keys())
