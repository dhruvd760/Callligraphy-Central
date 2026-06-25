import pytest
import sys
import os
import json
from typing import List, Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from critic.base_critic import BaseCritic
from critic.critic_registry import CriticRegistry
from critic.critic_executor import CriticExecutor
from critic.critic_agent import CriticAgent

from reflection.base_reflection import BaseReflection
from reflection.reflection_registry import ReflectionRegistry
from reflection.reflection_executor import ReflectionExecutor
from reflection.reflection_agent import ReflectionAgent

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
class DummyCritic(BaseCritic):
    @property
    def critic_name(self) -> str:
        return "dummy_critic"
    def evaluate(self, candidate: Any) -> Any:
        if candidate == "crash":
            raise ValueError("Intentional critic crash")
        return {
            "score": 9.5,
            "feedback": f"Critique of {candidate}"
        }

def test_base_critic_contract():
    class InvalidCritic(BaseCritic):
        pass
    with pytest.raises(TypeError):
        InvalidCritic()

def test_critic_registry():
    registry = CriticRegistry()
    critic = DummyCritic()
    
    registry.register(critic)
    assert registry.list_critics() == ["dummy_critic"]
    
    assert registry.get("dummy_critic") is critic
    assert registry.get("missing") is None

def test_critic_executor():
    executor = CriticExecutor()
    critic = DummyCritic()
    
    # Valid
    res = executor.execute_critique("test data", critic)
    assert res["critique"]["score"] == 9.5
    assert res["critique"]["feedback"] == "Critique of test data"
    
    # Error
    res_err = executor.execute_critique("crash", critic)
    assert "error" in res_err
    assert "Intentional critic crash" in res_err["error"]

def test_critic_agent():
    registry = CriticRegistry()
    registry.register(DummyCritic())
    
    executor = CriticExecutor()
    ctx = ContextManager()
    agent = CriticAgent(registry, executor, ctx)
    
    # Valid
    req = json.dumps({"critic_name": "dummy_critic", "candidate": "test candidate"})
    res = agent.process(req)
    assert res["status"] == "success"
    assert res["critic"] == "dummy_critic"
    assert res["result"]["score"] == 9.5
    assert res["result"]["feedback"] == "Critique of test candidate"
    
    # Missing critic
    res_miss = agent.process(json.dumps({"critic_name": "missing"}))
    assert res_miss == {"error": "Critic source 'missing' not found."}
    
    # Missing name
    res_no_name = agent.process("{}")
    assert res_no_name == {"error": "No 'critic_name' provided in request."}
    
    # Invalid JSON
    res_inv = agent.process("not json")
    assert res_inv == {"error": "Invalid critic request format. Expected JSON."}

def test_mega_integration():
    ctx = ContextManager()
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
    
    # 3. Router & 4. Planner
    class MegaPlanA(BasePlan):
        @property
        def plan_name(self) -> str:
            return "mega_plan_a"
        def build(self, request: str) -> List[str]:
            return ["prompt_agent", "extractor", "tool_agent"]

    plan_registry = PlannerRegistry()
    plan_registry.register(MegaPlanA())
    planner_executor = PlannerExecutor(agent_registry, ctx)
    
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
    
    # 5. Prompt & 6. Extractor & 7. Tool
    prompt_reg = PromptRegistry()
    prompt_reg.register(PromptTemplate("mega_prompt", "Prompt Output: {info}"))
    prompt_agent = PromptAgent(prompt_reg, ctx)
    agent_registry.register(prompt_agent)
    
    class ExtractAgent(BaseAgent):
        @property
        def agent_name(self) -> str:
            return "extractor"
        def process(self, request: str) -> str:
            return json.dumps({"tool_name": "sim_tool", "args": {}})
    agent_registry.register(ExtractAgent())
    
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
    
    # 8. Workflow & 9. Memory (Abstracted/simulated effectively in orchestrator sequence)
    # The Orchestrator leverages ContextManager inherently as Memory.
    # The ADKAdapter runs these sequentially forming a pseudo-workflow.

    # 10. Conversation
    class MockConv(BaseConversation):
        @property
        def conversation_name(self) -> str:
            return "dummy_conversation"
        def respond(self, message: str, history: list) -> Any:
            return f"Response: {message}"

    conv_registry = ConversationRegistry()
    conv_registry.register(MockConv())
    
    class LocalMockContextManager:
        def get_recent_history(self):
            return []
    local_ctx = LocalMockContextManager()
    
    conv_executor = ConversationExecutor(local_ctx)
    conv_agent = ConversationAgent(conv_registry, conv_executor, local_ctx)
    agent_registry.register(conv_agent)
    
    # 11. Reflection
    class DummyReflection(BaseReflection):
        @property
        def reflection_name(self) -> str:
            return "dummy_reflection"
        def analyze(self, input_data: Any) -> Any:
            return {"quality": "good", "summary": str(input_data)}
            
    ref_registry = ReflectionRegistry()
    ref_registry.register(DummyReflection())
    ref_executor = ReflectionExecutor()
    ref_agent = ReflectionAgent(ref_registry, ref_executor, ctx)
    agent_registry.register(ref_agent)
    
    # 12. Critic
    crit_registry = CriticRegistry()
    crit_registry.register(DummyCritic())
    crit_executor = CriticExecutor()
    crit_agent = CriticAgent(crit_registry, crit_executor, ctx)
    agent_registry.register(crit_agent)
    
    # ---------------- EXECUTION PIPELINE ----------------

    adk_adapter = ADKAdapter(agent_registry, ctx)
    
    # Step A: Knowledge
    know_adk = adk_adapter.adapt("knowledge_agent")
    res_know = know_adk.run(json.dumps({"knowledge_name": "dummy_knowledge", "query": "universe"}))
    info = res_know["result"]["result"] if isinstance(res_know.get("result"), dict) else res_know.get("result")
    
    # Step B: Reasoner
    reason_adk = adk_adapter.adapt("reasoning_agent")
    res_reason = reason_adk.run(json.dumps({"reasoner_name": "dummy_reasoner", "request": "think"}))
    route_name = "smart_mega_route"
    
    # Step C: Router -> Planner -> Prompt -> Extractor -> Tool (Execution workflow block)
    orchestrator = AgentOrchestrator(agent_registry, ctx)
    router_req = json.dumps({
        "route_name": route_name,
        "request": json.dumps({"prompt_name": "mega_prompt", "args": {"info": info}})
    })
    res_orch = orchestrator.execute_sequential(router_req, ["router_agent"])
    router_output = res_orch["router_agent"]["result"]["result"]
    
    # Step D: Conversation
    conv_req = json.dumps({
        "conversation_name": "dummy_conversation", 
        "message": f"Tool says: {router_output}"
    })
    res_conv = orchestrator.execute_sequential(conv_req, ["conversation_agent"])
    conv_output = res_conv["conversation_agent"]["result"]["response"]
    
    # Step E: Reflection
    ref_req = json.dumps({
        "reflection_name": "dummy_reflection",
        "input": conv_output
    })
    res_ref = orchestrator.execute_sequential(ref_req, ["reflection_agent"])
    ref_output = res_ref["reflection_agent"]["result"]
    
    # Step F: Critic
    crit_req = json.dumps({
        "critic_name": "dummy_critic",
        "candidate": ref_output
    })
    res_crit = orchestrator.execute_sequential(crit_req, ["critic_agent"])
    
    # Verifications
    assert res_crit["critic_agent"]["status"] == "success"
    assert res_crit["critic_agent"]["result"]["score"] == 9.5
    assert "quality': 'good'" in str(res_crit["critic_agent"]["result"]["feedback"])
