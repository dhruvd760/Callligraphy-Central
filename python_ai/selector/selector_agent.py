import json
import sys
import os
from typing import Optional, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agents.base_agent import BaseAgent
from memory.context_manager import ContextManager
from .selector_registry import SelectorRegistry
from .selector_executor import SelectorExecutor

class SelectorAgent(BaseAgent):
    """
    A specialized BaseAgent capable of processing selection securely.
    """
    def __init__(self, selector_registry: SelectorRegistry, selector_executor: SelectorExecutor, context_manager: Optional[ContextManager] = None):
        super().__init__(context_manager)
        self.selector_registry = selector_registry
        self.selector_executor = selector_executor

    @property
    def agent_name(self) -> str:
        return "selector_agent"

    def process(self, request: str) -> Any:
        try:
            parsed = self.parse_request(request)
            selector_name = parsed.get("selector_name")
            candidates = parsed.get("candidates")

            if not selector_name:
                return {"error": "No 'selector_name' provided in request."}

            selector = self.selector_registry.get(selector_name)
            if selector is None:
                return {"error": f"Selector source '{selector_name}' not found."}

            exec_res = self.selector_executor.execute_select(candidates, selector)
            
            if isinstance(exec_res, dict) and "error" in exec_res:
                return exec_res
                
            return {
                "status": "success",
                "selector": selector_name,
                "result": exec_res.get("select_result")
            }

        except json.JSONDecodeError:
            return {"error": "Invalid selector request format. Expected JSON."}
        except Exception as e:
            return {"error": str(e)}
