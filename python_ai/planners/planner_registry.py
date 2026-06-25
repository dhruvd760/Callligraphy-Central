from typing import Dict, Optional, List
from .base_plan import BasePlan

class PlannerRegistry:
    """Localized catalog of available plans."""
    
    def __init__(self):
        self._plans: Dict[str, BasePlan] = {}

    def register(self, plan: BasePlan) -> None:
        """Registers a plan by its plan_name."""
        self._plans[plan.plan_name] = plan

    def get(self, name: str) -> Optional[BasePlan]:
        """Retrieves a registered plan safely returning None if missing."""
        return self._plans.get(name)

    def list_plans(self) -> List[str]:
        """Returns the keys of all registered plans."""
        return list(self._plans.keys())
