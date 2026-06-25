from typing import Dict, Optional, List
from .base_scorer import BaseScorer

class ScorerRegistry:
    """Localized catalog of available scorer components."""
    
    def __init__(self):
        self._scorers: Dict[str, BaseScorer] = {}

    def register(self, scorer: BaseScorer) -> None:
        """Registers a scorer by its scorer_name."""
        self._scorers[scorer.scorer_name] = scorer

    def get(self, name: str) -> Optional[BaseScorer]:
        """Retrieves a registered scorer safely returning None if missing."""
        return self._scorers.get(name)

    def list_scorers(self) -> List[str]:
        """Returns the keys of all registered scorer blocks."""
        return list(self._scorers.keys())
