from typing import Any
from .base_scorer import BaseScorer

class ScorerExecutor:
    """Executes scoring securely against a candidate block."""
    
    def execute_score(self, candidate: Any, scorer: BaseScorer) -> Any:
        try:
            result = scorer.score(candidate)
            return {"score_result": result}
        except Exception as e:
            return {"error": f"Scorer execution failed for '{scorer.scorer_name}': {str(e)}"}
