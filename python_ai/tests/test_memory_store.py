import pytest
import sys
import os
import json
from typing import List, Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from memory_store.base_memory_store import BaseMemoryStore
from memory_store.memory_store_registry import MemoryStoreRegistry
from memory_store.memory_store_executor import MemoryStoreExecutor
from memory_store.memory_store_agent import MemoryStoreAgent

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
class DummyMemoryStore(BaseMemoryStore):
    def __init__(self):
        self._db = {}
        
    @property
    def memory_store_name(self) -> str:
        return "dummy_store"
        
    def save(self, key: str, value: Any) -> None:
        if key == "crash":
            raise ValueError("Intentional memory save crash")
        self._db[key] = value
        
    def load(self, key: str) -> Any:
        if key == "crash_load":
            raise ValueError("Intentional memory load crash")
        return self._db.get(key)

def test_base_memory_store_contract():
    class InvalidStore(BaseMemoryStore):
        pass
    with pytest.raises(TypeError):
        InvalidStore()

def test_memory_store_registry():
    registry = MemoryStoreRegistry()
    store = DummyMemoryStore()
    
    registry.register(store)
    assert registry.list_memory_stores() == ["dummy_store"]
    
    assert registry.get("dummy_store") is store
    assert registry.get("missing") is None

def test_memory_store_executor():
    executor = MemoryStoreExecutor()
    store = DummyMemoryStore()
    
    # Valid Save
    res_save = executor.execute_save("test_key", "test_value", store)
    assert res_save["status"] == "success"
    assert res_save["operation"] == "save"
    
    # Valid Load
    res_load = executor.execute_load("test_key", store)
    assert res_load["status"] == "success"
    assert res_load["value"] == "test_value"
    
    # Save Error
    res_save_err = executor.execute_save("crash", "val", store)
    assert "error" in res_save_err
    assert "Intentional memory save crash" in res_save_err["error"]
    
    # Load Error
    res_load_err = executor.execute_load("crash_load", store)
    assert "error" in res_load_err
    assert "Intentional memory load crash" in res_load_err["error"]

def test_memory_store_agent():
    registry = MemoryStoreRegistry()
    registry.register(DummyMemoryStore())
    
    executor = MemoryStoreExecutor()
    ctx = ContextManager()
    agent = MemoryStoreAgent(registry, executor, ctx)
    
    # Valid Save
    req_save = json.dumps({
        "memory_store_name": "dummy_store", 
        "operation": "save",
        "key": "agent_key",
        "value": "agent_val"
    })
    res_save = agent.process(req_save)
    assert res_save["status"] == "success"
    assert res_save["memory_store"] == "dummy_store"
    assert res_save["result"]["operation"] == "save"
    
    # Valid Load
    req_load = json.dumps({
        "memory_store_name": "dummy_store", 
        "operation": "load",
        "key": "agent_key"
    })
    res_load = agent.process(req_load)
    assert res_load["status"] == "success"
    assert res_load["result"]["value"] == "agent_val"
    
    # Missing operation
    res_no_op = agent.process(json.dumps({"memory_store_name": "dummy_store", "key": "k"}))
    assert res_no_op == {"error": "No 'operation' provided in request."}
    
    # Missing key
    res_no_key = agent.process(json.dumps({"memory_store_name": "dummy_store", "operation": "load"}))
    assert res_no_key == {"error": "No 'key' provided in request."}
    
    # Unknown operation
    res_bad_op = agent.process(json.dumps({"memory_store_name": "dummy_store", "operation": "fly", "key": "k"}))
    assert res_bad_op == {"error": "Unknown operation 'fly'."}
    
    # Missing store
    res_miss = agent.process(json.dumps({"memory_store_name": "missing", "operation": "load", "key": "k"}))
    assert res_miss == {"error": "Memory store 'missing' not found."}
    
    # Missing name
    res_no_name = agent.process("{}")
    assert res_no_name == {"error": "No 'memory_store_name' provided in request."}
    
    # Invalid JSON
    res_inv = agent.process("not json")
    assert res_inv == {"error": "Invalid memory store request format. Expected JSON."}

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
    class DummyCritic(BaseCritic):
        @property
        def critic_name(self) -> str:
            return "dummy_critic"
        def evaluate(self, candidate: Any) -> Any:
            return {"score": 9.5, "feedback": f"Critique of {candidate}"}
            
    crit_registry = CriticRegistry()
    crit_registry.register(DummyCritic())
    crit_executor = CriticExecutor()
    crit_agent = CriticAgent(crit_registry, crit_executor, ctx)
    agent_registry.register(crit_agent)
    
    # 13. Memory Store
    store_registry = MemoryStoreRegistry()
    store_registry.register(DummyMemoryStore())
    store_executor = MemoryStoreExecutor()
    store_agent = MemoryStoreAgent(store_registry, store_executor, ctx)
    agent_registry.register(store_agent)
    
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
    
    # Step C: Router -> Planner -> Prompt -> Extractor -> Tool
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
    crit_output = res_crit["critic_agent"]["result"]
    
    # Step G: Memory Store
    store_req = json.dumps({
        "memory_store_name": "dummy_store",
        "operation": "save",
        "key": "final_critique_result",
        "value": crit_output
    })
    res_store = orchestrator.execute_sequential(store_req, ["memory_store_agent"])
    
    # Verifications
    assert res_store["memory_store_agent"]["status"] == "success"
    assert res_store["memory_store_agent"]["result"]["operation"] == "save"
    
    # Load to verify
    store_load_req = json.dumps({
        "memory_store_name": "dummy_store",
        "operation": "load",
        "key": "final_critique_result"
    })
    res_load = orchestrator.execute_sequential(store_load_req, ["memory_store_agent"])
    
    loaded_val = res_load["memory_store_agent"]["result"]["value"]
    assert loaded_val["score"] == 9.5
    assert "quality" in str(loaded_val["feedback"])
