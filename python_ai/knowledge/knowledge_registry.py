from typing import Dict, Optional, List
from .base_knowledge import BaseKnowledge

class KnowledgeRegistry:
    """Localized catalog of available knowledge sources."""
    
    def __init__(self):
        self._knowledge_sources: Dict[str, BaseKnowledge] = {}

    def register(self, knowledge: BaseKnowledge) -> None:
        """Registers a knowledge source by its knowledge_name."""
        self._knowledge_sources[knowledge.knowledge_name] = knowledge

    def get(self, name: str) -> Optional[BaseKnowledge]:
        """Retrieves a registered knowledge source safely returning None if missing."""
        return self._knowledge_sources.get(name)

    def list_knowledge(self) -> List[str]:
        """Returns the keys of all registered knowledge sources."""
        return list(self._knowledge_sources.keys())
