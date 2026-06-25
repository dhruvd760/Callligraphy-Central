from typing import Dict, Optional, List
from .base_reasoner import BaseReasoner

class ReasonerRegistry:
    """Localized catalog of available reasoners."""
    
    def __init__(self):
        self._reasoners: Dict[str, BaseReasoner] = {}

    def register(self, reasoner: BaseReasoner) -> None:
        """Registers a reasoner by its reasoner_name."""
        self._reasoners[reasoner.reasoner_name] = reasoner

    def get(self, name: str) -> Optional[BaseReasoner]:
        """Retrieves a registered reasoner safely returning None if missing."""
        return self._reasoners.get(name)

    def list_reasoners(self) -> List[str]:
        """Returns the keys of all registered reasoners."""
        return list(self._reasoners.keys())
