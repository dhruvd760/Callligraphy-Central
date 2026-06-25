import json
import sys
import os
from typing import Optional, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agents.base_agent import BaseAgent
from memory.context_manager import ContextManager
from .evaluator_registry import EvaluatorRegistry
from .evaluator_executor import EvaluatorExecutor

class EvaluatorAgent(BaseAgent):
    """
    A specialized BaseAgent capable of processing evaluations securely.
    """
    def __init__(self, evaluator_registry: EvaluatorRegistry, evaluator_executor: EvaluatorExecutor, context_manager: Optional[ContextManager] = None):
        super().__init__(context_manager)
        self.evaluator_registry = evaluator_registry
        self.evaluator_executor = evaluator_executor

    @property
    def agent_name(self) -> str:
        return "evaluator_agent"

    def process(self, request: str) -> Any:
        try:
            parsed = self.parse_request(request)
            evaluator_name = parsed.get("evaluator_name")
            candidate = parsed.get("candidate")

            if not evaluator_name:
                return {"error": "No 'evaluator_name' provided in request."}

            evaluator = self.evaluator_registry.get(evaluator_name)
            if evaluator is None:
                return {"error": f"Evaluator source '{evaluator_name}' not found."}

            exec_res = self.evaluator_executor.execute_evaluation(candidate, evaluator)
            
            if isinstance(exec_res, dict) and "error" in exec_res:
                return exec_res
                
            return {
                "status": "success",
                "evaluator": evaluator_name,
                "result": exec_res.get("evaluation")
            }

        except json.JSONDecodeError:
            return {"error": "Invalid evaluator request format. Expected JSON."}
        except Exception as e:
            return {"error": str(e)}
