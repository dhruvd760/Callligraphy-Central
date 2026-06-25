from typing import Any
from .base_memory_store import BaseMemoryStore

class MemoryStoreExecutor:
    """Executes operations securely against a memory store."""
    
    def execute_save(self, key: str, value: Any, store: BaseMemoryStore) -> Any:
        try:
            store.save(key, value)
            return {"status": "success", "operation": "save"}
        except Exception as e:
            return {"error": f"Memory store save failed for '{store.memory_store_name}': {str(e)}"}

    def execute_load(self, key: str, store: BaseMemoryStore) -> Any:
        try:
            result = store.load(key)
            return {"status": "success", "operation": "load", "value": result}
        except Exception as e:
            return {"error": f"Memory store load failed for '{store.memory_store_name}': {str(e)}"}
