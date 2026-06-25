import json
import sys
import os
from typing import Optional, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.base_agent import BaseAgent
from memory.context_manager import ContextManager
from .planner_registry import PlannerRegistry
from .planner_executor import PlannerExecutor

class PlannerAgent(BaseAgent):
    """
    A specialized BaseAgent capable of parsing requests and executing
    dynamic plans safely through the PlannerRegistry.
    """
    def __init__(self, planner_registry: PlannerRegistry, planner_executor: PlannerExecutor, context_manager: Optional[ContextManager] = None):
        super().__init__(context_manager)
        self.planner_registry = planner_registry
        self.planner_executor = planner_executor

    @property
    def agent_name(self) -> str:
        return "planner_agent"

    def process(self, request: str) -> Any:
        try:
            parsed = self.parse_request(request)
            plan_name = parsed.get("plan_name")
            plan_request = parsed.get("request", "")

            if not plan_name:
                return {"error": "No 'plan_name' provided in request."}

            plan = self.planner_registry.get(plan_name)
            if plan is None:
                return {"error": f"Plan '{plan_name}' not found."}

            steps = plan.build(plan_request)
            result = self.planner_executor.execute_plan(plan_request, steps)
            
            return {
                "status": "success",
                "plan": plan_name,
                "steps": steps,
                "result": result
            }

        except json.JSONDecodeError:
            return {"error": "Invalid planner request format. Expected JSON."}
        except Exception as e:
            return {"error": str(e)}
