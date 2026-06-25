import json
from .tool_executor import MCPToolExecutor

class MCPServer:
    """
    Lightweight Model Context Protocol (MCP) server representation.
    """
    def __init__(self, tool_executor: MCPToolExecutor):
        self.tool_executor = tool_executor

    def handle_request(self, request: str) -> str:
        """
        Handles an incoming JSON string request and returns a JSON string response.
        """
        result = self.tool_executor.execute(request)
        return json.dumps(result)
