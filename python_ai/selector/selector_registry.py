from typing import Dict, Optional, List
from .base_selector import BaseSelector

class SelectorRegistry:
    """Localized catalog of available selector components."""
    
    def __init__(self):
        self._selectors: Dict[str, BaseSelector] = {}

    def register(self, selector: BaseSelector) -> None:
        """Registers a selector by its selector_name."""
        self._selectors[selector.selector_name] = selector

    def get(self, name: str) -> Optional[BaseSelector]:
        """Retrieves a registered selector safely returning None if missing."""
        return self._selectors.get(name)

    def list_selectors(self) -> List[str]:
        """Returns the keys of all registered selector blocks."""
        return list(self._selectors.keys())
