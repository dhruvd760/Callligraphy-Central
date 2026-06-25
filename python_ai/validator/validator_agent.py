import json
import sys
import os
from typing import Optional, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agents.base_agent import BaseAgent
from memory.context_manager import ContextManager
from .validator_registry import ValidatorRegistry
from .validator_executor import ValidatorExecutor

class ValidatorAgent(BaseAgent):
    """
    A specialized BaseAgent capable of processing validations securely.
    """
    def __init__(self, validator_registry: ValidatorRegistry, validator_executor: ValidatorExecutor, context_manager: Optional[ContextManager] = None):
        super().__init__(context_manager)
        self.validator_registry = validator_registry
        self.validator_executor = validator_executor

    @property
    def agent_name(self) -> str:
        return "validator_agent"

    def process(self, request: str) -> Any:
        try:
            parsed = self.parse_request(request)
            validator_name = parsed.get("validator_name")
            candidate = parsed.get("candidate")

            if not validator_name:
                return {"error": "No 'validator_name' provided in request."}

            validator = self.validator_registry.get(validator_name)
            if validator is None:
                return {"error": f"Validator source '{validator_name}' not found."}

            exec_res = self.validator_executor.execute_validation(candidate, validator)
            
            if isinstance(exec_res, dict) and "error" in exec_res:
                return exec_res
                
            return {
                "status": "success",
                "validator": validator_name,
                "result": exec_res.get("validation")
            }

        except json.JSONDecodeError:
            return {"error": "Invalid validator request format. Expected JSON."}
        except Exception as e:
            return {"error": str(e)}
