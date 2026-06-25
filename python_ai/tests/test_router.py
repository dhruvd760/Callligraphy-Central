import pytest
import sys
import os
import json
from typing import List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
class AppendAgentA(BaseAgent):
    @property
    def agent_name(self) -> str:
        return "agent_a"
    def process(self, request: str) -> str:
        return request + " -> A"

class AppendAgentB(BaseAgent):
    @property
    def agent_name(self) -> str:
        return "agent_b"
    def process(self, request: str) -> str:
        return request + " -> B"
        
class MockPlanA(BasePlan):
    @property
    def plan_name(self) -> str:
        return "plan_a"
    def build(self, request: str) -> List[str]:
        return ["agent_a"]

class MockPlanB(BasePlan):
    @property
    def plan_name(self) -> str:
        return "plan_b"
    def build(self, request: str) -> List[str]:
        return ["agent_a", "agent_b"]

class SmartRoute(BaseRoute):
    @property
    def route_name(self) -> str:
        return "smart_route"
    def select(self, request: str) -> str:
        if "B" in request:
            return "plan_b"
        return "plan_a"

class BadRoute(BaseRoute):
    @property
    def route_name(self) -> str:
        return "bad_route"
    def select(self, request: str) -> str:
        return "missing_plan"


def test_base_route_contract():
    class InvalidRoute(BaseRoute):
        pass
    with pytest.raises(TypeError):
        InvalidRoute()

def test_route_registry():
    registry = RouteRegistry()
    route = SmartRoute()
    
    registry.register(route)
    assert registry.list_routes() == ["smart_route"]
    
    assert registry.get("smart_route") is route
    assert registry.get("missing") is None

def test_route_executor():
    agent_registry = AgentRegistry()
    agent_registry.register(AppendAgentA())
    agent_registry.register(AppendAgentB())
    ctx = ContextManager()
    planner_executor = PlannerExecutor(agent_registry, ctx)
    
    planner_registry = PlannerRegistry()
    planner_registry.register(MockPlanA())
    planner_registry.register(MockPlanB())
    
    route_executor = RouteExecutor(planner_registry, planner_executor)
    
    route = SmartRoute()
    
    # Selects plan_a
    res_a = route_executor.execute_route("Start", route)
    assert res_a["selected_plan"] == "plan_a"
    assert res_a["result"] == "Start -> A"
    
    # Selects plan_b
    res_b = route_executor.execute_route("Start B", route)
    assert res_b["selected_plan"] == "plan_b"
    assert res_b["result"] == "Start B -> A -> B"
    
    # Missing plan
    bad_route = BadRoute()
    res_bad = route_executor.execute_route("Start", bad_route)
    assert "error" in res_bad
    assert "missing plan" in res_bad["error"]

def test_router_agent():
    agent_registry = AgentRegistry()
    agent_registry.register(AppendAgentA())
    ctx = ContextManager()
    planner_executor = PlannerExecutor(agent_registry, ctx)
    planner_registry = PlannerRegistry()
    planner_registry.register(MockPlanA())
    
    route_executor = RouteExecutor(planner_registry, planner_executor)
    route_registry = RouteRegistry()
    route_registry.register(SmartRoute())
    
    router_agent = RouterAgent(route_registry, route_executor, ctx)
    
    # Valid call
    req = json.dumps({"route_name": "smart_route", "request": "Go"})
    res = router_agent.process(req)
    assert res["status"] == "success"
    assert res["route"] == "smart_route"
    assert res["selected_plan"] == "plan_a"
    assert res["result"] == "Go -> A"
    
    # Invalid JSON
    res_inv = router_agent.process("not json")
    assert res_inv == {"error": "Invalid router request format. Expected JSON."}
    
    # Missing route_name
    res_no_name = router_agent.process("{}")
    assert res_no_name == {"error": "No 'route_name' provided in request."}
    
    # Missing route
    res_missing = router_agent.process(json.dumps({"route_name": "miss", "request": "Go"}))
    assert res_missing == {"error": "Route 'miss' not found."}

def test_mega_integration():
    ctx = ContextManager()
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
            return ["prompt_agent"] # Shorter route
            
    plan_registry = PlannerRegistry()
    plan_registry.register(MegaPlanA())
    plan_registry.register(MegaPlanB())
    
    # 5. SmartRoute
    class SmartMegaRoute(BaseRoute):
        @property
        def route_name(self) -> str:
            return "smart_mega_route"
        def select(self, request: str) -> str:
            if "mega" in request:
                return "mega_plan_a"
            return "mega_plan_b"
            
    route_registry = RouteRegistry()
    route_registry.register(SmartMegaRoute())
    
    # Core Engines
    planner_executor = PlannerExecutor(agent_registry, ctx)
    route_executor = RouteExecutor(plan_registry, planner_executor)
    
    # Router Agent
    router_agent = RouterAgent(route_registry, route_executor, ctx)
    agent_registry.register(router_agent)
    
    # ADK Adapter
    adk_adapter = ADKAdapter(agent_registry, ctx)
    adk_agent = adk_adapter.adapt("router_agent")
    
    # Orchestrator
    orchestrator = AgentOrchestrator(agent_registry, ctx)
    
    # Execution Payload
    req = json.dumps({"route_name": "smart_mega_route", "request": json.dumps({"prompt_name": "mega_prompt", "mega": True})})
    
    # Test ADK Execution
    res_adk = adk_agent.run(req)
    assert res_adk["status"] == "success"
    assert res_adk["selected_plan"] == "mega_plan_a"
    assert res_adk["result"]["result"] == "Mega Tool Success"
    
    # Test Orchestrator Execution
    res_orch = orchestrator.execute_sequential(req, ["router_agent"])
    assert res_orch["router_agent"]["status"] == "success"
    assert res_orch["router_agent"]["selected_plan"] == "mega_plan_a"
    assert res_orch["router_agent"]["result"]["result"] == "Mega Tool Success"
