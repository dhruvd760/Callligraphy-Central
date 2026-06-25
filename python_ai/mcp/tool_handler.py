import json
from typing import Any
from .tool_registry import MCPToolRegistry
from .tool_executor import MCPToolExecutor

class MCPToolHandler:
    """
    Handles incoming MCP tool requests securely by routing them to the executor.
    """
    def __init__(self, tool_registry: MCPToolRegistry, tool_executor: MCPToolExecutor):
        self.tool_registry = tool_registry
        self.tool_executor = tool_executor

    def process_request(self, request: str) -> Any:
        return self.tool_executor.execute(request)
