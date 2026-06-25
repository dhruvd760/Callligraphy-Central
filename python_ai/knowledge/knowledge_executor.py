import sys
import os
from typing import Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from .base_knowledge import BaseKnowledge

class KnowledgeExecutor:
    """Executes a query against a selected knowledge source."""
    
    def execute_lookup(self, query: str, knowledge: BaseKnowledge) -> Any:
        try:
            result = knowledge.lookup(query)
            return {"knowledge": result}
        except Exception as e:
            return {"error": f"Knowledge lookup failed for '{knowledge.knowledge_name}': {str(e)}"}
