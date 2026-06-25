import pytest
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from adk.base_adk_agent import BaseADKAgent
from adk.adk_registry import ADKRegistry
from adk.adk_adapter import ADKAdapter
from agents.base_agent import BaseAgent
from agents.agent_registry import AgentRegistry
from agents.orchestrator import AgentOrchestrator
from memory.context_manager import ContextManager
from tools.base_tool import BaseTool
from tools.tool_registry import ToolRegistry
from tools.tool_agent import ToolAgent

class MockADKAgent(BaseADKAgent):
    @property
    def agent_name(self) -> str:
        return "mock_adk"
    def run(self, request: str) -> str:
        return f"ADK run: {request}"

class MockBaseAgent(BaseAgent):
    @property
    def agent_name(self) -> str:
        return "mock_base"
    def process(self, request: str) -> str:
        return f"Base process: {request}"

class MockCalcTool(BaseTool):
    @property
    def tool_name(self) -> str:
        return "calc"
    def execute(self, **kwargs) -> int:
        return 42

def test_base_adk_agent_contract():
    class InvalidADKAgent(BaseADKAgent):
        pass
    with pytest.raises(TypeError):
        InvalidADKAgent()

def test_adk_registry():
    registry = ADKRegistry()
    agent = MockADKAgent()
    
    registry.register(agent)
    assert registry.list_agents() == ["mock_adk"]
    
    retrieved = registry.get("mock_adk")
    assert retrieved is agent
    
    missing = registry.get("missing")
    assert missing is None

def test_adk_adapter():
    agent_registry = AgentRegistry()
    agent = MockBaseAgent()
    agent_registry.register(agent)
    
    context_manager = ContextManager()
    adapter = ADKAdapter(agent_registry, context_manager)
    
    adk_agent = adapter.adapt("mock_base")
    assert adk_agent is not None
    assert adk_agent.agent_name == "mock_base"
    
    # Verify run delegates to process
    res = adk_agent.run("test request")
    assert res == "Base process: test request"
    
    # Missing agent handling
    missing_adk = adapter.adapt("missing")
    assert missing_adk is None

def test_tool_agent_compatibility():
    tool_registry = ToolRegistry()
    tool_registry.register(MockCalcTool())
    
    tool_agent = ToolAgent(tool_registry)
    agent_registry = AgentRegistry()
    agent_registry.register(tool_agent)
    
    context_manager = ContextManager()
    adapter = ADKAdapter(agent_registry, context_manager)
    
    adk_tool_agent = adapter.adapt("tool_agent")
    assert adk_tool_agent is not None
    
    # Call tool through ADK interface
    req = json.dumps({"tool_name": "calc"})
    res = adk_tool_agent.run(req)
    assert res == {"status": "success", "tool": "calc", "result": 42}
