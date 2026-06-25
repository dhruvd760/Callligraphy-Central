import sys
import os
from typing import Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from planners.planner_registry import PlannerRegistry
from planners.planner_executor import PlannerExecutor
from .base_route import BaseRoute

class RouteExecutor:
    """Executes a route by determining the correct plan and handing it to the PlannerExecutor."""
    
    def __init__(self, planner_registry: PlannerRegistry, planner_executor: PlannerExecutor):
        self.planner_registry = planner_registry
        self.planner_executor = planner_executor

    def execute_route(self, request: str, route: BaseRoute) -> Any:
        try:
            plan_name = route.select(request)
            plan = self.planner_registry.get(plan_name)
            
            if plan is None:
                return {"error": f"Route '{route.route_name}' selected missing plan '{plan_name}'."}
                
            steps = plan.build(request)
            result = self.planner_executor.execute_plan(request, steps)
            
            return {
                "selected_plan": plan_name,
                "result": result
            }
        except Exception as e:
            return {"error": f"Route execution failed for '{route.route_name}': {str(e)}"}
