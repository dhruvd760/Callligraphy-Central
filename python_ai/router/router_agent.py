import json
import sys
import os
from typing import Optional, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agents.base_agent import BaseAgent
from memory.context_manager import ContextManager
from .route_registry import RouteRegistry
from .route_executor import RouteExecutor

class RouterAgent(BaseAgent):
    """
    A specialized BaseAgent capable of parsing requests and securely executing
    conditional execution routes.
    """
    def __init__(self, route_registry: RouteRegistry, route_executor: RouteExecutor, context_manager: Optional[ContextManager] = None):
        super().__init__(context_manager)
        self.route_registry = route_registry
        self.route_executor = route_executor

    @property
    def agent_name(self) -> str:
        return "router_agent"

    def process(self, request: str) -> Any:
        try:
            parsed = self.parse_request(request)
            route_name = parsed.get("route_name")
            route_request = parsed.get("request", "")

            if not route_name:
                return {"error": "No 'route_name' provided in request."}

            route = self.route_registry.get(route_name)
            if route is None:
                return {"error": f"Route '{route_name}' not found."}

            exec_res = self.route_executor.execute_route(route_request, route)
            
            if isinstance(exec_res, dict) and "error" in exec_res:
                return exec_res
                
            return {
                "status": "success",
                "route": route_name,
                "selected_plan": exec_res.get("selected_plan"),
                "result": exec_res.get("result")
            }

        except json.JSONDecodeError:
            return {"error": "Invalid router request format. Expected JSON."}
        except Exception as e:
            return {"error": str(e)}
