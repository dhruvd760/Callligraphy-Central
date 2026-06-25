import json
import sys
import os
from typing import Optional, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agents.base_agent import BaseAgent
from memory.context_manager import ContextManager
from .knowledge_registry import KnowledgeRegistry
from .knowledge_executor import KnowledgeExecutor

class KnowledgeAgent(BaseAgent):
    """
    A specialized BaseAgent capable of parsing queries and retrieving 
    information securely from knowledge bases.
    """
    def __init__(self, knowledge_registry: KnowledgeRegistry, knowledge_executor: KnowledgeExecutor, context_manager: Optional[ContextManager] = None):
        super().__init__(context_manager)
        self.knowledge_registry = knowledge_registry
        self.knowledge_executor = knowledge_executor

    @property
    def agent_name(self) -> str:
        return "knowledge_agent"

    def process(self, request: str) -> Any:
        try:
            parsed = self.parse_request(request)
            knowledge_name = parsed.get("knowledge_name")
            query = parsed.get("query", "")

            if not knowledge_name:
                return {"error": "No 'knowledge_name' provided in request."}

            knowledge = self.knowledge_registry.get(knowledge_name)
            if knowledge is None:
                return {"error": f"Knowledge source '{knowledge_name}' not found."}

            exec_res = self.knowledge_executor.execute_lookup(query, knowledge)
            
            if isinstance(exec_res, dict) and "error" in exec_res:
                return exec_res
                
            return {
                "status": "success",
                "knowledge_source": knowledge_name,
                "result": exec_res.get("knowledge")
            }

        except json.JSONDecodeError:
            return {"error": "Invalid knowledge request format. Expected JSON."}
        except Exception as e:
            return {"error": str(e)}
