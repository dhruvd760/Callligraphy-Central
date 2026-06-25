from typing import Dict, Optional, List
from .base_tool import BaseMCPTool

class MCPToolRegistry:
    """Localized catalog of available MCP tool components."""
    
    def __init__(self):
        self._tools: Dict[str, BaseMCPTool] = {}

    def register(self, tool: BaseMCPTool) -> None:
        """Registers a tool by its tool_name."""
        self._tools[tool.tool_name] = tool

    def get(self, name: str) -> Optional[BaseMCPTool]:
        """Retrieves a registered tool safely returning None if missing."""
        return self._tools.get(name)

    def list_tools(self) -> List[str]:
        """Returns the keys of all registered MCP tools."""
        return list(self._tools.keys())
