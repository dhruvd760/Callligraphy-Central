import time
from typing import List, Dict, Any

class SessionMemory:
    """Maintains a ledger of recent requests and their resulting metadata."""
    
    def __init__(self):
        self._history: List[Dict[str, Any]] = []

    def add_entry(self, request: str, metadata: dict) -> None:
        """Appends a new interaction entry to the session history."""
        self._history.append({
            'timestamp': time.time(),
            'request': request,
            'metadata': metadata
        })

    def get_recent_entries(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Returns the most recent N entries."""
        return self._history[-limit:] if limit > 0 else []

    def clear(self) -> None:
        """Clears the session history."""
        self._history = []
