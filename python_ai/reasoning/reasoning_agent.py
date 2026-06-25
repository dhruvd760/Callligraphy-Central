import json
import sys
import os
from typing import Optional, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agents.base_agent import BaseAgent
from memory.context_manager import ContextManager
from .reasoner_registry import ReasonerRegistry
from .reasoning_executor import ReasoningExecutor

class ReasoningAgent(BaseAgent):
    """
    A specialized BaseAgent capable of parsing requests and executing
    context-aware reasoning logic safely.
    """
    def __init__(self, reasoner_registry: ReasonerRegistry, reasoning_executor: ReasoningExecutor, context_manager: Optional[ContextManager] = None):
        super().__init__(context_manager)
        self.reasoner_registry = reasoner_registry
        self.reasoning_executor = reasoning_executor

    @property
    def agent_name(self) -> str:
        return "reasoning_agent"

    def process(self, request: str) -> Any:
        try:
            parsed = self.parse_request(request)
            reasoner_name = parsed.get("reasoner_name")
            reasoner_request = parsed.get("request", "")

            if not reasoner_name:
                return {"error": "No 'reasoner_name' provided in request."}

            reasoner = self.reasoner_registry.get(reasoner_name)
            if reasoner is None:
                return {"error": f"Reasoner '{reasoner_name}' not found."}

            exec_res = self.reasoning_executor.execute_reasoning(reasoner_request, reasoner)
            
            if isinstance(exec_res, dict) and "error" in exec_res:
                return exec_res
                
            return {
                "status": "success",
                "reasoner": reasoner_name,
                "result": exec_res
            }

        except json.JSONDecodeError:
            return {"error": "Invalid reasoning request format. Expected JSON."}
        except Exception as e:
            return {"error": str(e)}
