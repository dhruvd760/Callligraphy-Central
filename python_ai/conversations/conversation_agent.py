import json
import sys
import os
from typing import Optional, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agents.base_agent import BaseAgent
from memory.context_manager import ContextManager
from .conversation_registry import ConversationRegistry
from .conversation_executor import ConversationExecutor

class ConversationAgent(BaseAgent):
    """
    A specialized BaseAgent capable of processing conversational
    messages safely.
    """
    def __init__(self, conversation_registry: ConversationRegistry, conversation_executor: ConversationExecutor, context_manager: Optional[ContextManager] = None):
        super().__init__(context_manager)
        self.conversation_registry = conversation_registry
        self.conversation_executor = conversation_executor

    @property
    def agent_name(self) -> str:
        return "conversation_agent"

    def process(self, request: str) -> Any:
        try:
            parsed = self.parse_request(request)
            conversation_name = parsed.get("conversation_name")
            message = parsed.get("message", "")

            if not conversation_name:
                return {"error": "No 'conversation_name' provided in request."}

            conversation = self.conversation_registry.get(conversation_name)
            if conversation is None:
                return {"error": f"Conversation source '{conversation_name}' not found."}

            exec_res = self.conversation_executor.execute_conversation(message, conversation)
            
            if isinstance(exec_res, dict) and "error" in exec_res:
                return exec_res
                
            return {
                "status": "success",
                "conversation": conversation_name,
                "result": exec_res
            }

        except json.JSONDecodeError:
            return {"error": "Invalid conversation request format. Expected JSON."}
        except Exception as e:
            return {"error": str(e)}
