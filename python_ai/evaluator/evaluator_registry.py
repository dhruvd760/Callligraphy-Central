from typing import Dict, Optional, List
from .base_evaluator import BaseEvaluator

class EvaluatorRegistry:
    """Localized catalog of available evaluator components."""
    
    def __init__(self):
        self._evaluators: Dict[str, BaseEvaluator] = {}

    def register(self, evaluator: BaseEvaluator) -> None:
        """Registers an evaluator by its evaluator_name."""
        self._evaluators[evaluator.evaluator_name] = evaluator

    def get(self, name: str) -> Optional[BaseEvaluator]:
        """Retrieves a registered evaluator safely returning None if missing."""
        return self._evaluators.get(name)

    def list_evaluators(self) -> List[str]:
        """Returns the keys of all registered evaluator blocks."""
        return list(self._evaluators.keys())
