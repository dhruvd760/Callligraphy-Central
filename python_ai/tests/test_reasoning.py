import pytest
import sys
import os
import json
from typing import List, Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from reasoning.base_reasoner import BaseReasoner
from reasoning.reasoner_registry import ReasonerRegistry
from reasoning.reasoning_executor import ReasoningExecutor
from reasoning.reasoning_agent import ReasoningAgent

from router.base_route import BaseRoute
from router.route_registry import RouteRegistry
from router.route_executor import RouteExecutor
from router.router_agent import RouterAgent

from planners.base_plan import BasePlan
from planners.planner_registry import PlannerRegistry
from planners.planner_executor import PlannerExecutor

from agents.base_agent import BaseAgent
from agents.agent_registry import AgentRegistry
from agents.orchestrator import AgentOrchestrator
from memory.context_manager import ContextManager
from adk.adk_adapter import ADKAdapter
from tools.base_tool import BaseTool
from tools.tool_registry import ToolRegistry
from tools.tool_agent import ToolAgent
from prompts.prompt_template import PromptTemplate
from prompts.prompt_registry import PromptRegistry
from prompts.prompt_agent import PromptAgent

# Mocks
class MockContextManager:
    def build_context(self):
        return {"user_prefs": "dark_mode"}

class DummyReasoner(BaseReasoner):
    @property
    def reasoner_name(self) -> str:
        return "dummy_reasoner"
    def reason(self, request: str, memory_context: Any) -> Dict[str, Any]:
        return {"selected_route": "smart_mega_route"}

class ErrorReasoner(BaseReasoner):
    @property
    def reasoner_name(self) -> str:
        return "error_reasoner"
    def reason(self, request: str, memory_context: Any) -> Dict[str, Any]:
        raise ValueError("Intentional reasoning crash")


def test_base_reasoner_contract():
    class InvalidReasoner(BaseReasoner):
        pass
    with pytest.raises(TypeError):
        InvalidReasoner()

def test_reasoner_registry():
    registry = ReasonerRegistry()
    reasoner = DummyReasoner()
    
    registry.register(reasoner)
    assert registry.list_reasoners() == ["dummy_reasoner"]
    
    assert registry.get("dummy_reasoner") is reasoner
    assert registry.get("missing") is None

def test_reasoning_executor():
    ctx = MockContextManager()
    executor = ReasoningExecutor(ctx)
    
    # Valid
    reasoner = DummyReasoner()
    res = executor.execute_reasoning("test", reasoner)
    assert res["context"] == {"user_prefs": "dark_mode"}
    assert res["decision"]["selected_route"] == "smart_mega_route"
    
    # Error
    err_reasoner = ErrorReasoner()
    res_err = executor.execute_reasoning("test", err_reasoner)
    assert "error" in res_err
    assert "Intentional reasoning crash" in res_err["error"]

def test_reasoning_agent():
    registry = ReasonerRegistry()
    registry.register(DummyReasoner())
    
    ctx = MockContextManager()
    executor = ReasoningExecutor(ctx)
    
    agent = ReasoningAgent(registry, executor, ctx)
    
    # Valid
    req = json.dumps({"reasoner_name": "dummy_reasoner", "request": "think"})
    res = agent.process(req)
    assert res["status"] == "success"
    assert res["reasoner"] == "dummy_reasoner"
    assert res["result"]["decision"]["selected_route"] == "smart_mega_route"
    
    # Missing reasoner
    res_miss = agent.process(json.dumps({"reasoner_name": "missing"}))
    assert res_miss == {"error": "Reasoner 'missing' not found."}
    
    # Missing name
    res_no_name = agent.process("{}")
    assert res_no_name == {"error": "No 'reasoner_name' provided in request."}
    
    # Invalid JSON
    res_inv = agent.process("not json")
    assert res_inv == {"error": "Invalid reasoning request format. Expected JSON."}

def test_mega_integration():
    ctx = MockContextManager()
    agent_registry = AgentRegistry()
    
    # 1. ToolAgent
    class SimpleTool(BaseTool):
        @property
        def tool_name(self) -> str:
            return "sim_tool"
        def execute(self, **kwargs):
            return "Mega Tool Success"
    tool_reg = ToolRegistry()
    tool_reg.register(SimpleTool())
    tool_agent = ToolAgent(tool_reg, ctx)
    agent_registry.register(tool_agent)
    
    # 2. PromptAgent
    prompt_reg = PromptRegistry()
    prompt_reg.register(PromptTemplate("mega_prompt", "Prompt Output"))
    prompt_agent = PromptAgent(prompt_reg, ctx)
    agent_registry.register(prompt_agent)
    
    # 3. Extractor
    class ExtractAgent(BaseAgent):
        @property
        def agent_name(self) -> str:
            return "extractor"
        def process(self, request: str) -> str:
            return json.dumps({"tool_name": "sim_tool", "args": {}})
    agent_registry.register(ExtractAgent())
    
    # 4. Planners
    class MegaPlanA(BasePlan):
        @property
        def plan_name(self) -> str:
            return "mega_plan_a"
        def build(self, request: str) -> List[str]:
            return ["prompt_agent", "extractor", "tool_agent"]

    class MegaPlanB(BasePlan):
        @property
        def plan_name(self) -> str:
            return "mega_plan_b"
        def build(self, request: str) -> List[str]:
            return ["prompt_agent"]
            
    plan_registry = PlannerRegistry()
    plan_registry.register(MegaPlanA())
    plan_registry.register(MegaPlanB())
    planner_executor = PlannerExecutor(agent_registry, ctx)
    
    # 5. Route
    class SmartMegaRoute(BaseRoute):
        @property
        def route_name(self) -> str:
            return "smart_mega_route"
        def select(self, request: str) -> str:
            return "mega_plan_a"
            
    route_registry = RouteRegistry()
    route_registry.register(SmartMegaRoute())
    route_executor = RouteExecutor(plan_registry, planner_executor)
    router_agent = RouterAgent(route_registry, route_executor, ctx)
    agent_registry.register(router_agent)
    
    # 6. Reasoner
    reasoner_registry = ReasonerRegistry()
    reasoner_registry.register(DummyReasoner())
    reasoning_executor = ReasoningExecutor(ctx)
    reasoning_agent = ReasoningAgent(reasoner_registry, reasoning_executor, ctx)
    agent_registry.register(reasoning_agent)

    # Wrap in ADKAdapter (for orchestrator execution simulation)
    adk_adapter = ADKAdapter(agent_registry, ctx)
    adk_agent = adk_adapter.adapt("reasoning_agent")
    
    # Execution Payload for Reasoner
    req = json.dumps({"reasoner_name": "dummy_reasoner", "request": "think"})
    
    # Run reasoner via ADK
    res_reason = adk_agent.run(req)
    route_name = res_reason["result"]["decision"]["selected_route"]
    
    # Construct Router Payload
    router_req = json.dumps({
        "route_name": route_name,
        "request": json.dumps({"prompt_name": "mega_prompt"})
    })
    
    # Orchestrator
    orchestrator = AgentOrchestrator(agent_registry, ctx)
    
    # Test Orchestrator Execution
    res_orch = orchestrator.execute_sequential(router_req, ["router_agent"])
    
    # The final output is from router_agent
    assert res_orch["router_agent"]["status"] == "success"
    assert res_orch["router_agent"]["route"] == "smart_mega_route"
    assert res_orch["router_agent"]["selected_plan"] == "mega_plan_a"
    assert res_orch["router_agent"]["result"]["result"] == "Mega Tool Success"
