import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from memory.session_memory import SessionMemory
from memory.user_preferences import UserPreferences
from memory.context_manager import ContextManager

def test_session_memory():
    sm = SessionMemory()
    sm.add_entry("req1", {"tag": "A"})
    sm.add_entry("req2", {"tag": "B"})
    
    entries = sm.get_recent_entries(1)
    assert len(entries) == 1
    assert entries[0]['request'] == "req2"
    
    sm.clear()
    assert len(sm.get_recent_entries()) == 0

def test_user_preferences():
    up = UserPreferences()
    up.update_preferences(language="English", tags=["calligraphy"])
    
    prefs = up.get_preferences()
    assert prefs['language'] == "English"
    assert prefs['tags'] == ["calligraphy"]
    assert prefs['style'] is None
    
    up.update_preferences(style="Copperplate")
    prefs = up.get_preferences()
    assert prefs['style'] == "Copperplate"

def test_context_manager():
    cm = ContextManager()
    cm.user_preferences.update_preferences(language="French")
    cm.session_memory.add_entry("How do I flourish?", {"tags": ["flourishing"]})
    
    context_str = cm.build_context()
    
    assert "--- BEGIN CONTEXT ---" in context_str
    assert "French" in context_str
    assert "How do I flourish?" in context_str
    assert "flourishing" in context_str
    
    cm.clear_context()
    assert len(cm.session_memory.get_recent_entries()) == 0
