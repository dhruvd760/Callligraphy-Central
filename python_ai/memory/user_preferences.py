from typing import List, Dict, Any, Optional

class UserPreferences:
    """Localized store for user-specific configurations that can persist across sessions."""
    
    def __init__(self):
        self._prefs: Dict[str, Any] = {
            'language': None,
            'style': None,
            'tags': []
        }

    def update_preferences(self, language: Optional[str] = None, style: Optional[str] = None, tags: Optional[List[str]] = None) -> None:
        """Safely updates provided preference keys."""
        if language is not None:
            self._prefs['language'] = language
        if style is not None:
            self._prefs['style'] = style
        if tags is not None:
            self._prefs['tags'] = tags

    def get_preferences(self) -> Dict[str, Any]:
        """Returns a copy of the current preferences."""
        return self._prefs.copy()
