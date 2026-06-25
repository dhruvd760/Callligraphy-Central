import json
from typing import Optional, Any
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.base_agent import BaseAgent
from memory.context_manager import ContextManager
from .tool_registry import ToolRegistry

class ToolAgent(BaseAgent):
    """
    A specialized BaseAgent capable of parsing tool-calling requests and delegating to ToolRegistry.
    """
    def __init__(self, tool_registry: ToolRegistry, context_manager: Optional[ContextManager] = None):
        super().__init__(context_manager)
        self.tool_registry = tool_registry

    @property
    def agent_name(self) -> str:
        return "tool_agent"

    def process(self, request: str) -> Any:
        try:
            # Expecting request to be a JSON string describing the tool call.
            parsed = self.parse_request(request)
            tool_name = parsed.get("tool_name")
            kwargs = parsed.get("args", {})
            
            if not tool_name:
                return {"error": "No 'tool_name' provided in request."}
                
            tool = self.tool_registry.get(tool_name)
            if tool is None:
                return {"error": f"Tool '{tool_name}' not found."}
                
            result = tool.execute(**kwargs)
            return {"status": "success", "tool": tool_name, "result": result}
            
        except json.JSONDecodeError:
            return {"error": "Invalid tool call request format. Expected JSON."}
        except Exception as e:
            return {"error": str(e)}
