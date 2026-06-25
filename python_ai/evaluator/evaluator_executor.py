from typing import Any
from .base_evaluator import BaseEvaluator

class EvaluatorExecutor:
    """Executes an evaluation against a candidate block."""
    
    def execute_evaluation(self, candidate: Any, evaluator: BaseEvaluator) -> Any:
        try:
            result = evaluator.evaluate(candidate)
            return {"evaluation": result}
        except Exception as e:
            return {"error": f"Evaluator execution failed for '{evaluator.evaluator_name}': {str(e)}"}
