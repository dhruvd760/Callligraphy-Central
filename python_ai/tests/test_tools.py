import pytest
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.base_tool import BaseTool
from tools.tool_registry import ToolRegistry
from tools.tool_agent import ToolAgent
from agents.orchestrator import AgentOrchestrator
from agents.agent_registry import AgentRegistry
from memory.context_manager import ContextManager

class MockAdditionTool(BaseTool):
    @property
    def tool_name(self) -> str:
        return "add"
        
    def execute(self, **kwargs) -> int:
        return kwargs.get("x", 0) + kwargs.get("y", 0)

def test_base_tool_contract():
    class InvalidTool(BaseTool):
        pass
    with pytest.raises(TypeError):
        InvalidTool()

def test_tool_registry():
    registry = ToolRegistry()
    tool = MockAdditionTool()
    
    registry.register(tool)
    assert registry.list_tools() == ["add"]
    
    retrieved = registry.get("add")
    assert retrieved is tool
    
    assert registry.get("missing") is None

def test_tool_agent():
    tool_registry = ToolRegistry()
    tool_registry.register(MockAdditionTool())
    agent = ToolAgent(tool_registry)
    
    # Valid call
    req = json.dumps({"tool_name": "add", "args": {"x": 5, "y": 10}})
    res = agent.process(req)
    assert res == {"status": "success", "tool": "add", "result": 15}
    
    # Missing tool call
    req_missing = json.dumps({"tool_name": "missing"})
    res_missing = agent.process(req_missing)
    assert res_missing == {"error": "Tool 'missing' not found."}
    
    # Invalid JSON
    res_invalid = agent.process("not a json")
    assert res_invalid == {"error": "Invalid tool call request format. Expected JSON."}
    
    # Missing tool_name param
    res_no_name = agent.process("{}")
    assert res_no_name == {"error": "No 'tool_name' provided in request."}

def test_tool_agent_in_orchestrator():
    tool_registry = ToolRegistry()
    tool_registry.register(MockAdditionTool())
    
    agent_registry = AgentRegistry()
    tool_agent = ToolAgent(tool_registry)
    agent_registry.register(tool_agent)
    
    context_manager = ContextManager()
    orchestrator = AgentOrchestrator(agent_registry, context_manager)
    
    req = json.dumps({"tool_name": "add", "args": {"x": 2, "y": 3}})
    responses = orchestrator.execute_sequential(req, ["tool_agent"])
    
    assert responses["tool_agent"]["result"] == 5
