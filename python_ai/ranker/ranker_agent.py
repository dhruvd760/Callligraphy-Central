import json
import sys
import os
from typing import Optional, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agents.base_agent import BaseAgent
from memory.context_manager import ContextManager
from .ranker_registry import RankerRegistry
from .ranker_executor import RankerExecutor

class RankerAgent(BaseAgent):
    """
    A specialized BaseAgent capable of processing rank operations securely.
    """
    def __init__(self, ranker_registry: RankerRegistry, ranker_executor: RankerExecutor, context_manager: Optional[ContextManager] = None):
        super().__init__(context_manager)
        self.ranker_registry = ranker_registry
        self.ranker_executor = ranker_executor

    @property
    def agent_name(self) -> str:
        return "ranker_agent"

    def process(self, request: str) -> Any:
        try:
            parsed = self.parse_request(request)
            ranker_name = parsed.get("ranker_name")
            candidates = parsed.get("candidates")

            if not ranker_name:
                return {"error": "No 'ranker_name' provided in request."}

            ranker = self.ranker_registry.get(ranker_name)
            if ranker is None:
                return {"error": f"Ranker source '{ranker_name}' not found."}

            exec_res = self.ranker_executor.execute_rank(candidates, ranker)
            
            if isinstance(exec_res, dict) and "error" in exec_res:
                return exec_res
                
            return {
                "status": "success",
                "ranker": ranker_name,
                "result": exec_res.get("rank_result")
            }

        except json.JSONDecodeError:
            return {"error": "Invalid ranker request format. Expected JSON."}
        except Exception as e:
            return {"error": str(e)}
