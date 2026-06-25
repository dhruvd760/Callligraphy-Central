import json
import sys
import os
from typing import Optional, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.base_agent import BaseAgent
from memory.context_manager import ContextManager
from .workflow_registry import WorkflowRegistry

class WorkflowAgent(BaseAgent):
    """
    A specialized BaseAgent capable of parsing requests and executing
    workflows safely through the WorkflowRegistry.
    """
    def __init__(self, workflow_registry: WorkflowRegistry, context_manager: Optional[ContextManager] = None):
        super().__init__(context_manager)
        self.workflow_registry = workflow_registry

    @property
    def agent_name(self) -> str:
        return "workflow_agent"

    def process(self, request: str) -> Any:
        try:
            parsed = self.parse_request(request)
            workflow_name = parsed.get("workflow_name")
            workflow_request = parsed.get("request", "")

            if not workflow_name:
                return {"error": "No 'workflow_name' provided in request."}

            workflow = self.workflow_registry.get(workflow_name)
            if workflow is None:
                return {"error": f"Workflow '{workflow_name}' not found."}

            result = workflow.execute(workflow_request)
            
            return {
                "status": "success",
                "workflow": workflow_name,
                "result": result
            }

        except json.JSONDecodeError:
            return {"error": "Invalid workflow request format. Expected JSON."}
        except Exception as e:
            return {"error": str(e)}
