import pytest
import json
import sys
import os
from typing import Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcp.base_tool import BaseMCPTool
from mcp.tool_registry import MCPToolRegistry
from mcp.tool_executor import MCPToolExecutor
from mcp.tool_handler import MCPToolHandler
from mcp.server import MCPServer

class DummyMCPTool(BaseMCPTool):
    @property
    def tool_name(self) -> str:
        return "dummy_mcp_tool"

    def execute(self, **kwargs: Any) -> Any:
        if kwargs.get("crash"):
            raise ValueError("Intentional MCP tool crash")
        return {"output": "MCP Success", "kwargs_received": kwargs}

def test_base_mcp_tool_contract():
    class InvalidTool(BaseMCPTool):
        pass
    with pytest.raises(TypeError):
        InvalidTool()

def test_mcp_tool_registry():
    registry = MCPToolRegistry()
    tool = DummyMCPTool()
    registry.register(tool)
    
    assert registry.list_tools() == ["dummy_mcp_tool"]
    assert registry.get("dummy_mcp_tool") is tool
    assert registry.get("missing") is None

def test_mcp_tool_handler():
    registry = MCPToolRegistry()
    registry.register(DummyMCPTool())
    executor = MCPToolExecutor(registry)
    handler = MCPToolHandler(registry, executor)
    
    # Valid
    req = json.dumps({"tool": "dummy_mcp_tool", "arguments": {"arg1": "val1"}})
    res = handler.process_request(req)
    assert res["status"] == "success"
    assert res["tool"] == "dummy_mcp_tool"
    assert res["result"]["output"] == "MCP Success"
    
    # Missing tool
    req_miss = json.dumps({"tool": "missing", "arguments": {}})
    res_miss = handler.process_request(req_miss)
    assert res_miss == {"error": "MCP tool 'missing' not found."}
    
    # Missing name
    res_no_name = handler.process_request("{}")
    assert res_no_name == {"error": "No 'tool' provided in request."}
    
    # Invalid JSON
    res_inv = handler.process_request("not json")
    assert res_inv == {"error": "Invalid request format. Expected JSON."}

def test_mcp_server():
    registry = MCPToolRegistry()
    registry.register(DummyMCPTool())
    executor = MCPToolExecutor(registry)
    server = MCPServer(executor)
    
    req = json.dumps({"tool": "dummy_mcp_tool", "arguments": {"test": 123}})
    res_str = server.handle_request(req)
    res = json.loads(res_str)
    
    assert res["status"] == "success"
    assert res["result"]["kwargs_received"]["test"] == 123
