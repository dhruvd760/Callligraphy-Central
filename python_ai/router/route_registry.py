from typing import Dict, Optional, List
from .base_route import BaseRoute

class RouteRegistry:
    """Localized catalog of available routing logic."""
    
    def __init__(self):
        self._routes: Dict[str, BaseRoute] = {}

    def register(self, route: BaseRoute) -> None:
        """Registers a route by its route_name."""
        self._routes[route.route_name] = route

    def get(self, name: str) -> Optional[BaseRoute]:
        """Retrieves a registered route safely returning None if missing."""
        return self._routes.get(name)

    def list_routes(self) -> List[str]:
        """Returns the keys of all registered routes."""
        return list(self._routes.keys())
