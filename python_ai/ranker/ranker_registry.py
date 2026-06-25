from typing import Dict, Optional, List
from .base_ranker import BaseRanker

class RankerRegistry:
    """Localized catalog of available ranker components."""
    
    def __init__(self):
        self._rankers: Dict[str, BaseRanker] = {}

    def register(self, ranker: BaseRanker) -> None:
        """Registers a ranker by its ranker_name."""
        self._rankers[ranker.ranker_name] = ranker

    def get(self, name: str) -> Optional[BaseRanker]:
        """Retrieves a registered ranker safely returning None if missing."""
        return self._rankers.get(name)

    def list_rankers(self) -> List[str]:
        """Returns the keys of all registered ranker blocks."""
        return list(self._rankers.keys())
