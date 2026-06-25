import pytest
import json
import sys
import os
from typing import Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcp.tool_registry import MCPToolRegistry
from mcp.tool_executor import MCPToolExecutor
from mcp.server import MCPServer
from mcp.base_tool import BaseMCPTool

class AnalyzeCalligraphyTestTool(BaseMCPTool):
    @property
    def tool_name(self) -> str:
        return "analyze_calligraphy"
        
    def execute(self, **kwargs: Any) -> Any:
        if kwargs.get("crash"):
            raise Exception("Mock crash")
        return "Dummy analysis."

def test_server_receive_request():
    registry = MCPToolRegistry()
    registry.register(AnalyzeCalligraphyTestTool())
    executor = MCPToolExecutor(registry)
    server = MCPServer(executor)
    
    # Ensure it returns a string format of JSON
    req = json.dumps({
        "tool": "analyze_calligraphy",
        "arguments": {"test_arg": True}
    })
    
    response_str = server.handle_request(req)
    assert isinstance(response_str, str)
    
    response = json.loads(response_str)
    assert response["status"] == "success"
    assert response["tool"] == "analyze_calligraphy"
    assert response["result"] == "Dummy analysis."

def test_server_missing_tool():
    registry = MCPToolRegistry()
    executor = MCPToolExecutor(registry)
    server = MCPServer(executor)
    
    req = json.dumps({
        "tool": "non_existent_tool",
        "arguments": {}
    })
    
    response_str = server.handle_request(req)
    response = json.loads(response_str)
    assert "error" in response
    assert "not found" in response["error"]

def test_server_invalid_json():
    registry = MCPToolRegistry()
    executor = MCPToolExecutor(registry)
    server = MCPServer(executor)
    
    response_str = server.handle_request("malformed json : {")
    response = json.loads(response_str)
    assert "error" in response
    assert "Expected JSON" in response["error"]

def test_server_execution_crash():
    registry = MCPToolRegistry()
    registry.register(AnalyzeCalligraphyTestTool())
    executor = MCPToolExecutor(registry)
    server = MCPServer(executor)
    
    req = json.dumps({
        "tool": "analyze_calligraphy",
        "arguments": {"crash": True}
    })
    
    response_str = server.handle_request(req)
    response = json.loads(response_str)
    assert "error" in response
    assert "Mock crash" in response["error"]
