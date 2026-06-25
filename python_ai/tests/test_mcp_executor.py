import pytest
import json
import sys
import os
from typing import Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcp.base_tool import BaseMCPTool
from mcp.tool_registry import MCPToolRegistry
from mcp.tool_executor import MCPToolExecutor

class DummyMCPTool(BaseMCPTool):
    @property
    def tool_name(self) -> str:
        return "dummy_mcp_tool"

    def execute(self, **kwargs: Any) -> Any:
        if kwargs.get("crash"):
            raise ValueError("Intentional MCP tool crash")
        return {"output": "MCP Success", "kwargs_received": kwargs}

def test_executor_successful_execution():
    registry = MCPToolRegistry()
    registry.register(DummyMCPTool())
    executor = MCPToolExecutor(registry)
    
    req = json.dumps({"tool": "dummy_mcp_tool", "arguments": {"test": 123}})
    res = executor.execute(req)
    
    assert res["status"] == "success"
    assert res["tool"] == "dummy_mcp_tool"
    assert res["result"]["output"] == "MCP Success"
    assert res["result"]["kwargs_received"]["test"] == 123

def test_executor_missing_tool():
    registry = MCPToolRegistry()
    executor = MCPToolExecutor(registry)
    
    req = json.dumps({"tool": "missing", "arguments": {}})
    res = executor.execute(req)
    
    assert res == {"error": "MCP tool 'missing' not found."}

def test_executor_invalid_request():
    registry = MCPToolRegistry()
    executor = MCPToolExecutor(registry)
    
    res = executor.execute("invalid json")
    assert res == {"error": "Invalid request format. Expected JSON."}
    
    res_no_name = executor.execute("{}")
    assert res_no_name == {"error": "No 'tool' provided in request."}

def test_executor_tool_execution_failure():
    registry = MCPToolRegistry()
    registry.register(DummyMCPTool())
    executor = MCPToolExecutor(registry)
    
    req = json.dumps({"tool": "dummy_mcp_tool", "arguments": {"crash": True}})
    res = executor.execute(req)
    
    assert "error" in res
    assert "Intentional MCP tool crash" in res["error"]
