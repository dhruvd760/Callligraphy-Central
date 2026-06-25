import json
from .session_memory import SessionMemory
from .user_preferences import UserPreferences

class ContextManager:
    """Synthesizes data from SessionMemory and UserPreferences into a readable format for LLM agents."""
    
    def __init__(self, session_memory: SessionMemory = None, user_preferences: UserPreferences = None):
        self.session_memory = session_memory or SessionMemory()
        self.user_preferences = user_preferences or UserPreferences()

    def build_context(self) -> str:
        """Merges preference keys and recent session interactions into a formatted string payload."""
        prefs = self.user_preferences.get_preferences()
        recent_entries = self.session_memory.get_recent_entries()

        context_lines = ["--- BEGIN CONTEXT ---"]
        
        context_lines.append("User Preferences:")
        context_lines.append(json.dumps(prefs, indent=2))
        
        context_lines.append("\nRecent Session History:")
        if not recent_entries:
            context_lines.append("No recent interactions.")
        else:
            for i, entry in enumerate(recent_entries, 1):
                context_lines.append(f"\nInteraction {i}:")
                context_lines.append(f"Request: {entry.get('request', '')}")
                context_lines.append(f"Metadata: {json.dumps(entry.get('metadata', {}))}")
                
        context_lines.append("--- END CONTEXT ---")
        
        return "\n".join(context_lines)

    def clear_context(self) -> None:
        """Clears the session memory."""
        self.session_memory.clear()
