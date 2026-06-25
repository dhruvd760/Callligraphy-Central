import json
import sys
import os
from typing import Optional, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agents.base_agent import BaseAgent
from memory.context_manager import ContextManager
from .critic_registry import CriticRegistry
from .critic_executor import CriticExecutor

class CriticAgent(BaseAgent):
    """
    A specialized BaseAgent capable of evaluating candidate data securely.
    """
    def __init__(self, critic_registry: CriticRegistry, critic_executor: CriticExecutor, context_manager: Optional[ContextManager] = None):
        super().__init__(context_manager)
        self.critic_registry = critic_registry
        self.critic_executor = critic_executor

    @property
    def agent_name(self) -> str:
        return "critic_agent"

    def process(self, request: str) -> Any:
        try:
            parsed = self.parse_request(request)
            critic_name = parsed.get("critic_name")
            candidate = parsed.get("candidate")

            if not critic_name:
                return {"error": "No 'critic_name' provided in request."}

            critic = self.critic_registry.get(critic_name)
            if critic is None:
                return {"error": f"Critic source '{critic_name}' not found."}

            exec_res = self.critic_executor.execute_critique(candidate, critic)
            
            if isinstance(exec_res, dict) and "error" in exec_res:
                return exec_res
                
            return {
                "status": "success",
                "critic": critic_name,
                "result": exec_res.get("critique")
            }

        except json.JSONDecodeError:
            return {"error": "Invalid critic request format. Expected JSON."}
        except Exception as e:
            return {"error": str(e)}
