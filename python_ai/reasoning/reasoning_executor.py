import sys
import os
from typing import Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from memory.context_manager import ContextManager
from .base_reasoner import BaseReasoner

class ReasoningExecutor:
    """Fetches memory context and executes reasoning."""
    
    def __init__(self, context_manager: ContextManager):
        self.context_manager = context_manager

    def execute_reasoning(self, request: str, reasoner: BaseReasoner) -> Any:
        try:
            # Safely fetch context from ContextManager
            memory_context = {}
            if hasattr(self.context_manager, 'build_context'):
                memory_context = self.context_manager.build_context()
                
            decision = reasoner.reason(request, memory_context)
            
            return {
                "context": memory_context,
                "decision": decision
            }
        except Exception as e:
            return {"error": f"Reasoning execution failed for '{reasoner.reasoner_name}': {str(e)}"}
