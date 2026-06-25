import pytest
import sys
import os
import json
from typing import List, Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from conversations.base_conversation import BaseConversation
from conversations.conversation_registry import ConversationRegistry
from conversations.conversation_executor import ConversationExecutor
from conversations.conversation_agent import ConversationAgent

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

# Mocks
class MockContextManager:
    def get_recent_history(self):
        return ["hello", "how are you"]

class DummyConversation(BaseConversation):
    @property
    def conversation_name(self) -> str:
        return "dummy_conversation"
    def respond(self, message: str, history: list) -> Any:
        if message == "crash":
            raise ValueError("Intentional conversation crash")
        return f"Response to {message} with history len {len(history)}"

def test_base_conversation_contract():
    class InvalidConversation(BaseConversation):
        pass
    with pytest.raises(TypeError):
        InvalidConversation()

def test_conversation_registry():
    registry = ConversationRegistry()
    conv = DummyConversation()
    
    registry.register(conv)
    assert registry.list_conversations() == ["dummy_conversation"]
    
    assert registry.get("dummy_conversation") is conv
    assert registry.get("missing") is None

def test_conversation_executor():
    ctx = MockContextManager()
    executor = ConversationExecutor(ctx)
    conv = DummyConversation()
    
    # Valid
    res = executor.execute_conversation("test", conv)
    assert res["history"] == ["hello", "how are you"]
    assert "Response to test" in res["response"]
    
    # Error
    res_err = executor.execute_conversation("crash", conv)
    assert "error" in res_err
    assert "Intentional conversation crash" in res_err["error"]

def test_conversation_agent():
    registry = ConversationRegistry()
    registry.register(DummyConversation())
    
    ctx = MockContextManager()
    executor = ConversationExecutor(ctx)
    
    agent = ConversationAgent(registry, executor, ctx)
    
    # Valid
    req = json.dumps({"conversation_name": "dummy_conversation", "message": "hello world"})
    res = agent.process(req)
    assert res["status"] == "success"
    assert res["conversation"] == "dummy_conversation"
    assert "Response to hello world" in res["result"]["response"]
    
    # Missing conversation
    res_miss = agent.process(json.dumps({"conversation_name": "missing"}))
    assert res_miss == {"error": "Conversation source 'missing' not found."}
    
    # Missing name
    res_no_name = agent.process("{}")
    assert res_no_name == {"error": "No 'conversation_name' provided in request."}
    
    # Invalid JSON
    res_inv = agent.process("not json")
    assert res_inv == {"error": "Invalid conversation request format. Expected JSON."}

def test_mega_integration():
    ctx = ContextManager() # From real memory if available, otherwise mock
    agent_registry = AgentRegistry()
    
    # 1. Knowledge
    class DummyKnowledge(BaseKnowledge):
        @property
        def knowledge_name(self) -> str:
            return "dummy_knowledge"
        def lookup(self, query: str) -> Any:
            return f"Found answer for {query}"
            
    know_reg = KnowledgeRegistry()
    know_reg.register(DummyKnowledge())
    know_exec = KnowledgeExecutor()
    know_agent = KnowledgeAgent(know_reg, know_exec, ctx)
    agent_registry.register(know_agent)
    
    # 2. Reasoner
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
    
    # 3. Tool
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
    
    # 4. Prompt
    prompt_reg = PromptRegistry()
    prompt_reg.register(PromptTemplate("mega_prompt", "Prompt Output: {info}"))
    prompt_agent = PromptAgent(prompt_reg, ctx)
    agent_registry.register(prompt_agent)
    
    # 5. Extractor
    class ExtractAgent(BaseAgent):
        @property
        def agent_name(self) -> str:
            return "extractor"
        def process(self, request: str) -> str:
            return json.dumps({"tool_name": "sim_tool", "args": {}})
    agent_registry.register(ExtractAgent())
    
    # 6. Planners
    class MegaPlanA(BasePlan):
        @property
        def plan_name(self) -> str:
            return "mega_plan_a"
        def build(self, request: str) -> List[str]:
            return ["prompt_agent", "extractor", "tool_agent"]

    plan_registry = PlannerRegistry()
    plan_registry.register(MegaPlanA())
    planner_executor = PlannerExecutor(agent_registry, ctx)
    
    # 7. Route
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
    
    # 8. Conversation
    conv_registry = ConversationRegistry()
    conv_registry.register(DummyConversation())
    
    class LocalMockContextManager:
        def get_recent_history(self):
            return []
    local_ctx = LocalMockContextManager()
    
    conv_executor = ConversationExecutor(local_ctx)
    conv_agent = ConversationAgent(conv_registry, conv_executor, local_ctx)
    agent_registry.register(conv_agent)
    
    # Execute full sequence manually bridging data logically
    
    # Step A: Execute Knowledge
    adk_adapter = ADKAdapter(agent_registry, ctx)
    know_adk = adk_adapter.adapt("knowledge_agent")
    req_know = json.dumps({"knowledge_name": "dummy_knowledge", "query": "universe"})
    res_know = know_adk.run(req_know)
    info = res_know["result"]["result"] if isinstance(res_know.get("result"), dict) else res_know.get("result")
    
    # Step B: Execute Reasoner
    reason_adk = adk_adapter.adapt("reasoning_agent")
    req_reason = json.dumps({"reasoner_name": "dummy_reasoner", "request": "think"})
    res_reason = reason_adk.run(req_reason)
    route_name = "smart_mega_route" # mocked reasoning logic extraction
    
    # Step C: Router -> Planner -> Prompt -> Extractor -> Tool (Via Orchestrator)
    router_req = json.dumps({
        "route_name": route_name,
        "request": json.dumps({"prompt_name": "mega_prompt", "args": {"info": info}})
    })
    orchestrator = AgentOrchestrator(agent_registry, ctx)
    res_orch = orchestrator.execute_sequential(router_req, ["router_agent"])
    
    router_output = res_orch["router_agent"]["result"]["result"]
    assert router_output == "Mega Tool Success"
    
    # Step D: Conversation passes the result into a conversational interface
    conv_req = json.dumps({
        "conversation_name": "dummy_conversation", 
        "message": f"Did the tool succeed? {router_output}"
    })
    res_conv = orchestrator.execute_sequential(conv_req, ["conversation_agent"])
    
    assert res_conv["conversation_agent"]["status"] == "success"
    assert "Response to Did the tool succeed? Mega Tool Success" in res_conv["conversation_agent"]["result"]["response"]
