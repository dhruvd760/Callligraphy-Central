from typing import Dict, Optional, List
from .base_reflection import BaseReflection

class ReflectionRegistry:
    """Localized catalog of available reflection sources."""
    
    def __init__(self):
        self._reflections: Dict[str, BaseReflection] = {}

    def register(self, reflection: BaseReflection) -> None:
        """Registers a reflection instance by its reflection_name."""
        self._reflections[reflection.reflection_name] = reflection

    def get(self, name: str) -> Optional[BaseReflection]:
        """Retrieves a registered reflection instance safely returning None if missing."""
        return self._reflections.get(name)

    def list_reflections(self) -> List[str]:
        """Returns the keys of all registered reflection blocks."""
        return list(self._reflections.keys())
