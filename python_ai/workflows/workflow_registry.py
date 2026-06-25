from typing import Dict, Optional, List
from .base_workflow import BaseWorkflow

class WorkflowRegistry:
    """Localized catalog of available workflows."""
    
    def __init__(self):
        self._workflows: Dict[str, BaseWorkflow] = {}

    def register(self, workflow: BaseWorkflow) -> None:
        """Registers a workflow by its workflow_name."""
        self._workflows[workflow.workflow_name] = workflow

    def get(self, name: str) -> Optional[BaseWorkflow]:
        """Retrieves a registered workflow or safely returns None."""
        return self._workflows.get(name)

    def list_workflows(self) -> List[str]:
        """Returns the keys of all registered workflows."""
        return list(self._workflows.keys())
