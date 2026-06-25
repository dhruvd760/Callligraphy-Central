import json
from typing import Any, Dict
from .tool_registry import MCPToolRegistry

class MCPToolExecutor:
    """
    Executes MCP tools securely, locates the requested tool from the registry,
    and formats responses natively.
    """
    def __init__(self, registry: MCPToolRegistry):
        self.registry = registry

    def execute(self, request: str) -> Dict[str, Any]:
        """
        Parses a JSON request, locates the tool, executes it securely,
        and returns a JSON dictionary. Never raises exceptions.
        """
        try:
            parsed = json.loads(request)
            if not isinstance(parsed, dict):
                return {"error": "Invalid request format. Expected JSON dictionary."}
            tool_name = parsed.get("tool")
            kwargs = parsed.get("arguments", {})

            if not tool_name:
                return {"error": "No 'tool' provided in request."}

            tool = self.registry.get(tool_name)
            if not tool:
                return {"error": f"MCP tool '{tool_name}' not found."}

            try:
                result = tool.execute(**kwargs)
                return {
                    "status": "success",
                    "tool": tool_name,
                    "result": result
                }
            except Exception as e:
                return {"error": f"MCP tool execution failed for '{tool_name}': {str(e)}"}

        except json.JSONDecodeError:
            return {"error": "Invalid request format. Expected JSON."}
        except Exception as e:
            return {"error": str(e)}
