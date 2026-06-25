from typing import Any
from .base_ranker import BaseRanker

class RankerExecutor:
    """Executes ranking securely against candidates."""
    
    def execute_rank(self, candidates: Any, ranker: BaseRanker) -> Any:
        try:
            result = ranker.rank(candidates)
            return {"rank_result": result}
        except Exception as e:
            return {"error": f"Ranker execution failed for '{ranker.ranker_name}': {str(e)}"}
