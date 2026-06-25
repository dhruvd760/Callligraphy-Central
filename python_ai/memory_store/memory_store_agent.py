import json
import sys
import os
from typing import Optional, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agents.base_agent import BaseAgent
from memory.context_manager import ContextManager
from .memory_store_registry import MemoryStoreRegistry
from .memory_store_executor import MemoryStoreExecutor

class MemoryStoreAgent(BaseAgent):
    """
    A specialized BaseAgent capable of saving and loading data securely.
    """
    def __init__(self, memory_store_registry: MemoryStoreRegistry, memory_store_executor: MemoryStoreExecutor, context_manager: Optional[ContextManager] = None):
        super().__init__(context_manager)
        self.memory_store_registry = memory_store_registry
        self.memory_store_executor = memory_store_executor

    @property
    def agent_name(self) -> str:
        return "memory_store_agent"

    def process(self, request: str) -> Any:
        try:
            parsed = self.parse_request(request)
            store_name = parsed.get("memory_store_name")
            operation = parsed.get("operation")
            key = parsed.get("key")

            if not store_name:
                return {"error": "No 'memory_store_name' provided in request."}
            if not operation:
                return {"error": "No 'operation' provided in request."}
            if not key:
                return {"error": "No 'key' provided in request."}

            store = self.memory_store_registry.get(store_name)
            if store is None:
                return {"error": f"Memory store '{store_name}' not found."}

            if operation == "save":
                value = parsed.get("value")
                exec_res = self.memory_store_executor.execute_save(key, value, store)
            elif operation == "load":
                exec_res = self.memory_store_executor.execute_load(key, store)
            else:
                return {"error": f"Unknown operation '{operation}'."}
            
            if isinstance(exec_res, dict) and "error" in exec_res:
                return exec_res
                
            return {
                "status": "success",
                "memory_store": store_name,
                "result": exec_res
            }

        except json.JSONDecodeError:
            return {"error": "Invalid memory store request format. Expected JSON."}
        except Exception as e:
            return {"error": str(e)}
