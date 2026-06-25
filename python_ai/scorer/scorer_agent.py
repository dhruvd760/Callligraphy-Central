import json
import sys
import os
from typing import Optional, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agents.base_agent import BaseAgent
from memory.context_manager import ContextManager
from .scorer_registry import ScorerRegistry
from .scorer_executor import ScorerExecutor

class ScorerAgent(BaseAgent):
    """
    A specialized BaseAgent capable of processing scores securely.
    """
    def __init__(self, scorer_registry: ScorerRegistry, scorer_executor: ScorerExecutor, context_manager: Optional[ContextManager] = None):
        super().__init__(context_manager)
        self.scorer_registry = scorer_registry
        self.scorer_executor = scorer_executor

    @property
    def agent_name(self) -> str:
        return "scorer_agent"

    def process(self, request: str) -> Any:
        try:
            parsed = self.parse_request(request)
            scorer_name = parsed.get("scorer_name")
            candidate = parsed.get("candidate")

            if not scorer_name:
                return {"error": "No 'scorer_name' provided in request."}

            scorer = self.scorer_registry.get(scorer_name)
            if scorer is None:
                return {"error": f"Scorer source '{scorer_name}' not found."}

            exec_res = self.scorer_executor.execute_score(candidate, scorer)
            
            if isinstance(exec_res, dict) and "error" in exec_res:
                return exec_res
                
            return {
                "status": "success",
                "scorer": scorer_name,
                "result": exec_res.get("score_result")
            }

        except json.JSONDecodeError:
            return {"error": "Invalid scorer request format. Expected JSON."}
        except Exception as e:
            return {"error": str(e)}
