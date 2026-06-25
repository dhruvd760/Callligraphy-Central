import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.base_agent import BaseAgent
from agents.agent_registry import AgentRegistry
from agents.orchestrator import AgentOrchestrator
from memory.context_manager import ContextManager

class MockAgent1(BaseAgent):
    @property
    def agent_name(self) -> str:
        return "mock_1"
        
    def process(self, request: str) -> str:
        return f"Mock1 processed: {request}"

class MockAgent2(BaseAgent):
    @property
    def agent_name(self) -> str:
        return "mock_2"
        
    def process(self, request: str) -> dict:
        return {"result": f"Mock2 processed: {request}"}

def test_base_agent_contract():
    # Attempting to instantiate an incomplete agent should raise TypeError
    class InvalidAgent(BaseAgent):
        pass
    
    with pytest.raises(TypeError):
        InvalidAgent()

def test_agent_registry():
    registry = AgentRegistry()
    agent1 = MockAgent1()
    agent2 = MockAgent2()
    
    registry.register(agent1)
    registry.register(agent2)
    
    # Test list_agents
    assert sorted(registry.list_agents()) == ["mock_1", "mock_2"]
    
    # Test get successful
    retrieved = registry.get("mock_1")
    assert retrieved is agent1
    
    # Test get missing agent safely returns None
    missing = registry.get("missing_agent")
    assert missing is None

def test_orchestrator_sequential():
    registry = AgentRegistry()
    registry.register(MockAgent1())
    registry.register(MockAgent2())
    
    context_manager = ContextManager()
    orchestrator = AgentOrchestrator(registry, context_manager)
    
    # Requesting valid and missing agents
    responses = orchestrator.execute_sequential("Test Request", ["mock_1", "missing_agent", "mock_2"])
    
    assert responses["mock_1"] == "Mock1 processed: Test Request"
    assert responses["missing_agent"] == {"error": "Agent not found."}
    assert responses["mock_2"] == {"result": "Mock2 processed: Test Request"}
