from typing import Dict, Optional, List
from .base_conversation import BaseConversation

class ConversationRegistry:
    """Localized catalog of available conversation models."""
    
    def __init__(self):
        self._conversations: Dict[str, BaseConversation] = {}

    def register(self, conversation: BaseConversation) -> None:
        """Registers a conversation by its conversation_name."""
        self._conversations[conversation.conversation_name] = conversation

    def get(self, name: str) -> Optional[BaseConversation]:
        """Retrieves a registered conversation safely returning None if missing."""
        return self._conversations.get(name)

    def list_conversations(self) -> List[str]:
        """Returns the keys of all registered conversations."""
        return list(self._conversations.keys())
