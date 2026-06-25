from typing import Optional, List, Dict
from .base_tool import BaseTool

class ToolRegistry:
    """Localized catalog of available tools."""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Registers a tool by its tool_name."""
        self._tools[tool.tool_name] = tool

    def get(self, name: str) -> Optional[BaseTool]:
        """Retrieves a registered tool or safely returns None."""
        return self._tools.get(name)

    def list_tools(self) -> List[str]:
        """Returns the keys of all registered tools."""
        return list(self._tools.keys())
