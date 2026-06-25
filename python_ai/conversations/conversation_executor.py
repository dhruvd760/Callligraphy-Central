import sys
import os
from typing import Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from memory.context_manager import ContextManager
from .base_conversation import BaseConversation

class ConversationExecutor:
    """Fetches memory context and executes conversation response."""
    
    def __init__(self, context_manager: ContextManager):
        self.context_manager = context_manager

    def execute_conversation(self, message: str, conversation: BaseConversation) -> Any:
        try:
            history = []
            if hasattr(self.context_manager, 'get_recent_history'):
                history = self.context_manager.get_recent_history()
            elif hasattr(self.context_manager, 'build_context'):
                ctx = self.context_manager.build_context()
                if isinstance(ctx, dict):
                    history = ctx.get("history", [])
            
            response = conversation.respond(message, history)
            
            return {
                "history": history,
                "response": response
            }
        except Exception as e:
            return {"error": f"Conversation execution failed for '{conversation.conversation_name}': {str(e)}"}
