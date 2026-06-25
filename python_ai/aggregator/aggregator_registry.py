from typing import Dict, Optional, List
from .base_aggregator import BaseAggregator

class AggregatorRegistry:
    """Localized catalog of available aggregator components."""
    
    def __init__(self):
        self._aggregators: Dict[str, BaseAggregator] = {}

    def register(self, aggregator: BaseAggregator) -> None:
        """Registers an aggregator by its aggregator_name."""
        self._aggregators[aggregator.aggregator_name] = aggregator

    def get(self, name: str) -> Optional[BaseAggregator]:
        """Retrieves a registered aggregator safely returning None if missing."""
        return self._aggregators.get(name)

    def list_aggregators(self) -> List[str]:
        """Returns the keys of all registered aggregator blocks."""
        return list(self._aggregators.keys())
