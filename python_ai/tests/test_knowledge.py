import pytest
import sys
import os
import json
from typing import List, Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from knowledge.base_knowledge import BaseKnowledge
from knowledge.knowledge_registry import KnowledgeRegistry
from knowledge.knowledge_executor import KnowledgeExecutor
from knowledge.knowledge_agent import KnowledgeAgent

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

class DummyKnowledge(BaseKnowledge):
    @property
    def knowledge_name(self) -> str:
        return "dummy_knowledge"
    def lookup(self, query: str) -> Any:
        if query == "crash":
            raise ValueError("Intentional knowledge crash")
        return f"Found answer for {query}"

def test_base_knowledge_contract():
    class InvalidKnowledge(BaseKnowledge):
        pass
    with pytest.raises(TypeError):
        InvalidKnowledge()

def test_knowledge_registry():
    registry = KnowledgeRegistry()
    knowledge = DummyKnowledge()
    
    registry.register(knowledge)
    assert registry.list_knowledge() == ["dummy_knowledge"]
    assert registry.get("dummy_knowledge") is knowledge
    assert registry.get("missing") is None

def test_knowledge_executor():
    executor = KnowledgeExecutor()
    knowledge = DummyKnowledge()
    
    # Valid
    res = executor.execute_lookup("test", knowledge)
    assert res == {"knowledge": "Found answer for test"}
    
    # Error
    res_err = executor.execute_lookup("crash", knowledge)
    assert "error" in res_err
    assert "Intentional knowledge crash" in res_err["error"]

def test_knowledge_agent():
    registry = KnowledgeRegistry()
    registry.register(DummyKnowledge())
    executor = KnowledgeExecutor()
    agent = KnowledgeAgent(registry, executor)
    
    # Valid
    req = json.dumps({"knowledge_name": "dummy_knowledge", "query": "hello"})
    res = agent.process(req)
    assert res["status"] == "success"
    assert res["knowledge_source"] == "dummy_knowledge"
    assert res["result"] == "Found answer for hello"
    
    # Missing knowledge
    res_miss = agent.process(json.dumps({"knowledge_name": "missing"}))
    assert res_miss == {"error": "Knowledge source 'missing' not found."}
    
    # Missing name
    res_no_name = agent.process("{}")
    assert res_no_name == {"error": "No 'knowledge_name' provided in request."}
    
    # Invalid JSON
    res_inv = agent.process("not json")
    assert res_inv == {"error": "Invalid knowledge request format. Expected JSON."}

def test_mega_integration():
    ctx = ContextManager()
    agent_registry = AgentRegistry()
    
    # 1. Knowledge
    know_reg = KnowledgeRegistry()
    know_reg.register(DummyKnowledge())
    know_exec = KnowledgeExecutor()
    know_agent = KnowledgeAgent(know_reg, know_exec, ctx)
    agent_registry.register(know_agent)
    
    # 2. Tool
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
    
    # 3. Prompt
    prompt_reg = PromptRegistry()
    prompt_reg.register(PromptTemplate("mega_prompt", "Prompt Output: {info}"))
    prompt_agent = PromptAgent(prompt_reg, ctx)
    agent_registry.register(prompt_agent)
    
    # 4. Extractor
    class ExtractAgent(BaseAgent):
        @property
        def agent_name(self) -> str:
            return "extractor"
        def process(self, request: str) -> str:
            return json.dumps({"tool_name": "sim_tool", "args": {}})
    agent_registry.register(ExtractAgent())
    
    # 5. Planners
    class MegaPlanA(BasePlan):
        @property
        def plan_name(self) -> str:
            return "mega_plan_a"
        def build(self, request: str) -> List[str]:
            return ["prompt_agent", "extractor", "tool_agent"]

    plan_registry = PlannerRegistry()
    plan_registry.register(MegaPlanA())
    planner_executor = PlannerExecutor(agent_registry, ctx)
    
    # 6. Route
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
    
    # 7. Reasoner
    class DummyReasoner(BaseReasoner):
        @property
        def reasoner_name(self) -> str:
            return "dummy_reasoner"
        def reason(self, request: str, memory_context: Any) -> Dict[str, Any]:
            return {"selected_route": "smart_mega_route"}
            
    reasoner_registry = ReasonerRegistry()
    reasoner_registry.register(DummyReasoner())
    reasoning_executor = ReasoningExecutor(ctx)
    reasoning_agent = ReasoningAgent(reasoner_registry, reasoning_executor, ctx)
    agent_registry.register(reasoning_agent)

    # Execution Setup
    adk_adapter = ADKAdapter(agent_registry, ctx)
    
    # 8. Step 1: Execute Knowledge via ADK
    know_adk = adk_adapter.adapt("knowledge_agent")
    req_know = json.dumps({"knowledge_name": "dummy_knowledge", "query": "universe"})
    res_know = know_adk.run(req_know)
    
    # Extract info securely
    info = res_know.get("result")
    if isinstance(info, dict) and "result" in info:
        info = info["result"]
    
    # 9. Step 2: Execute Reasoner via ADK
    reason_adk = adk_adapter.adapt("reasoning_agent")
    req_reason = json.dumps({"reasoner_name": "dummy_reasoner", "request": "think"})
    res_reason = reason_adk.run(req_reason)
    
    # Extract decision safely
    reason_result = res_reason.get("result", {})
    if isinstance(reason_result, dict) and "decision" in reason_result:
        route_name = reason_result["decision"].get("selected_route")
    elif isinstance(reason_result, dict) and "result" in reason_result:
        route_name = reason_result["result"]["decision"]["selected_route"]
    else:
        route_name = "smart_mega_route"
    
    # 10. Step 3: Map and execute Router via Orchestrator
    router_req = json.dumps({
        "route_name": route_name,
        "request": json.dumps({"prompt_name": "mega_prompt", "args": {"info": info}})
    })
    
    orchestrator = AgentOrchestrator(agent_registry, ctx)
    res_orch = orchestrator.execute_sequential(router_req, ["router_agent"])
    
    # Final assertions
    assert res_orch["router_agent"]["status"] == "success"
    
    router_res = res_orch["router_agent"]["result"]
    if isinstance(router_res, dict) and "result" in router_res:
        assert router_res["result"] == "Mega Tool Success"
    else:
        assert router_res == "Mega Tool Success"
