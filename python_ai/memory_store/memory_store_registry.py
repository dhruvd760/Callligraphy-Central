from typing import Dict, Optional, List
from .base_memory_store import BaseMemoryStore

class MemoryStoreRegistry:
    """Localized catalog of available memory store components."""
    
    def __init__(self):
        self._stores: Dict[str, BaseMemoryStore] = {}

    def register(self, store: BaseMemoryStore) -> None:
        """Registers a memory store by its memory_store_name."""
        self._stores[store.memory_store_name] = store

    def get(self, name: str) -> Optional[BaseMemoryStore]:
        """Retrieves a registered memory store safely returning None if missing."""
        return self._stores.get(name)

    def list_memory_stores(self) -> List[str]:
        """Returns the keys of all registered memory store blocks."""
        return list(self._stores.keys())
