import pytest
import sys
import os
import json
from typing import List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from planners.base_plan import BasePlan
from planners.planner_registry import PlannerRegistry
from planners.planner_executor import PlannerExecutor
from planners.planner_agent import PlannerAgent

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
from workflows.workflow_agent import WorkflowAgent
from workflows.workflow_registry import WorkflowRegistry

# Mock Agents
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
        
class ErrorAgent(BaseAgent):
    @property
    def agent_name(self) -> str:
        return "error_agent"
    def process(self, request: str) -> str:
        raise ValueError("Intentional crash")

class MockPlan(BasePlan):
    @property
    def plan_name(self) -> str:
        return "mock_plan"
    def build(self, request: str) -> List[str]:
        return ["agent_a", "agent_b"]

def test_base_plan_contract():
    class InvalidPlan(BasePlan):
        pass
    with pytest.raises(TypeError):
        InvalidPlan()

def test_planner_registry():
    registry = PlannerRegistry()
    plan = MockPlan()
    
    registry.register(plan)
    assert registry.list_plans() == ["mock_plan"]
    
    assert registry.get("mock_plan") is plan
    assert registry.get("missing") is None

def test_planner_executor():
    agent_registry = AgentRegistry()
    agent_registry.register(AppendAgentA())
    agent_registry.register(AppendAgentB())
    agent_registry.register(ErrorAgent())
    
    ctx = ContextManager()
    executor = PlannerExecutor(agent_registry, ctx)
    
    # Sequential chaining
    res = executor.execute_plan("Start", ["agent_a", "agent_b"])
    assert res == "Start -> A -> B"
    
    # Missing agent skipped
    res_skip = executor.execute_plan("Start", ["agent_a", "missing", "agent_b"])
    assert res_skip == "Start -> A -> B"
    
    # Error handling
    res_err = executor.execute_plan("Start", ["agent_a", "error_agent", "agent_b"])
    assert "error" in res_err
    assert "Intentional crash" in res_err["error"]

def test_planner_agent():
    agent_registry = AgentRegistry()
    agent_registry.register(AppendAgentA())
    agent_registry.register(AppendAgentB())
    
    ctx = ContextManager()
    executor = PlannerExecutor(agent_registry, ctx)
    
    plan_registry = PlannerRegistry()
    plan_registry.register(MockPlan())
    
    planner_agent = PlannerAgent(plan_registry, executor, ctx)
    
    # Valid call
    req = json.dumps({"plan_name": "mock_plan", "request": "Start"})
    res = planner_agent.process(req)
    assert res["status"] == "success"
    assert res["plan"] == "mock_plan"
    assert res["steps"] == ["agent_a", "agent_b"]
    assert res["result"] == "Start -> A -> B"
    
    # Missing plan
    req_missing = json.dumps({"plan_name": "missing", "request": "Start"})
    res_missing = planner_agent.process(req_missing)
    assert res_missing == {"error": "Plan 'missing' not found."}
    
    # Missing name
    res_no_name = planner_agent.process("{}")
    assert res_no_name == {"error": "No 'plan_name' provided in request."}
    
    # Invalid JSON
    res_inv = planner_agent.process("not json")
    assert res_inv == {"error": "Invalid planner request format. Expected JSON."}

def test_mega_integration():
    ctx = ContextManager()
    agent_registry = AgentRegistry()
    
    # Tool Agent
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
    
    # Prompt Agent
    prompt_reg = PromptRegistry()
    prompt_reg.register(PromptTemplate("mega_prompt", "Prompt Output"))
    prompt_agent = PromptAgent(prompt_reg, ctx)
    agent_registry.register(prompt_agent)
    
    # Extractor
    class ExtractAgent(BaseAgent):
        @property
        def agent_name(self) -> str:
            return "extractor"
        def process(self, request: str) -> str:
            return json.dumps({"tool_name": "sim_tool", "args": {}})
    agent_registry.register(ExtractAgent())
    
    # Workflow Agent (unused directly in plan but registered to prove compatibility)
    wf_registry = WorkflowRegistry()
    wf_agent = WorkflowAgent(wf_registry, ctx)
    agent_registry.register(wf_agent)
    
    # MegaPlan
    class MegaPlan(BasePlan):
        @property
        def plan_name(self) -> str:
            return "mega_plan"
        def build(self, request: str) -> List[str]:
            return ["prompt_agent", "extractor", "tool_agent"]
            
    plan_registry = PlannerRegistry()
    plan_registry.register(MegaPlan())
    
    executor = PlannerExecutor(agent_registry, ctx)
    planner_agent = PlannerAgent(plan_registry, executor, ctx)
    agent_registry.register(planner_agent)
    
    # Execution
    req = json.dumps({"plan_name": "mega_plan", "request": json.dumps({"prompt_name": "mega_prompt"})})
    
    # Via ADK Adapter
    adk_adapter = ADKAdapter(agent_registry, ctx)
    adk_agent = adk_adapter.adapt("planner_agent")
    
    # Via Orchestrator
    orchestrator = AgentOrchestrator(agent_registry, ctx)
    
    # Test ADK
    res_adk = adk_agent.run(req)
    assert res_adk["status"] == "success"
    assert res_adk["result"]["status"] == "success"
    assert res_adk["result"]["result"] == "Mega Tool Success"
    
    # Test Orchestrator
    res_orch = orchestrator.execute_sequential(req, ["planner_agent"])
    assert res_orch["planner_agent"]["status"] == "success"
    assert res_orch["planner_agent"]["result"]["result"] == "Mega Tool Success"
