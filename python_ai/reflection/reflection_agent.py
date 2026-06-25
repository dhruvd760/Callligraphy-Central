import json
import sys
import os
from typing import Optional, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agents.base_agent import BaseAgent
from memory.context_manager import ContextManager
from .reflection_registry import ReflectionRegistry
from .reflection_executor import ReflectionExecutor

class ReflectionAgent(BaseAgent):
    """
    A specialized BaseAgent capable of parsing responses, analyzing them,
    and returning structured reflections safely.
    """
    def __init__(self, reflection_registry: ReflectionRegistry, reflection_executor: ReflectionExecutor, context_manager: Optional[ContextManager] = None):
        super().__init__(context_manager)
        self.reflection_registry = reflection_registry
        self.reflection_executor = reflection_executor

    @property
    def agent_name(self) -> str:
        return "reflection_agent"

    def process(self, request: str) -> Any:
        try:
            parsed = self.parse_request(request)
            reflection_name = parsed.get("reflection_name")
            input_data = parsed.get("input")

            if not reflection_name:
                return {"error": "No 'reflection_name' provided in request."}

            reflection = self.reflection_registry.get(reflection_name)
            if reflection is None:
                return {"error": f"Reflection source '{reflection_name}' not found."}

            exec_res = self.reflection_executor.execute_reflection(input_data, reflection)
            
            if isinstance(exec_res, dict) and "error" in exec_res:
                return exec_res
                
            return {
                "status": "success",
                "reflection": reflection_name,
                "result": exec_res.get("reflection")
            }

        except json.JSONDecodeError:
            return {"error": "Invalid reflection request format. Expected JSON."}
        except Exception as e:
            return {"error": str(e)}
