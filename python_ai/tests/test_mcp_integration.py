import pytest
import json
import sys
import os
from typing import Any, Dict, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 1. Base / Managers
from memory.context_manager import ContextManager
from agents.base_agent import BaseAgent
from agents.agent_registry import AgentRegistry
from agents.orchestrator import AgentOrchestrator
from adk.adk_adapter import ADKAdapter

# 2. Pipeline Components
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

from prompts.prompt_template import PromptTemplate
from prompts.prompt_registry import PromptRegistry
from prompts.prompt_agent import PromptAgent

from tools.base_tool import BaseTool
from tools.tool_registry import ToolRegistry
from tools.tool_agent import ToolAgent

from conversations.base_conversation import BaseConversation
from conversations.conversation_registry import ConversationRegistry
from conversations.conversation_executor import ConversationExecutor
from conversations.conversation_agent import ConversationAgent

from reflection.base_reflection import BaseReflection
from reflection.reflection_registry import ReflectionRegistry
from reflection.reflection_executor import ReflectionExecutor
from reflection.reflection_agent import ReflectionAgent

from critic.base_critic import BaseCritic
from critic.critic_registry import CriticRegistry
from critic.critic_executor import CriticExecutor
from critic.critic_agent import CriticAgent

from memory_store.base_memory_store import BaseMemoryStore
from memory_store.memory_store_registry import MemoryStoreRegistry
from memory_store.memory_store_executor import MemoryStoreExecutor
from memory_store.memory_store_agent import MemoryStoreAgent

from evaluator.base_evaluator import BaseEvaluator
from evaluator.evaluator_registry import EvaluatorRegistry
from evaluator.evaluator_executor import EvaluatorExecutor
from evaluator.evaluator_agent import EvaluatorAgent

from validator.base_validator import BaseValidator
from validator.validator_registry import ValidatorRegistry
from validator.validator_executor import ValidatorExecutor
from validator.validator_agent import ValidatorAgent

from scorer.base_scorer import BaseScorer
from scorer.scorer_registry import ScorerRegistry
from scorer.scorer_executor import ScorerExecutor
from scorer.scorer_agent import ScorerAgent

from ranker.base_ranker import BaseRanker
from ranker.ranker_registry import RankerRegistry
from ranker.ranker_executor import RankerExecutor
from ranker.ranker_agent import RankerAgent

from selector.base_selector import BaseSelector
from selector.selector_registry import SelectorRegistry
from selector.selector_executor import SelectorExecutor
from selector.selector_agent import SelectorAgent

from aggregator.base_aggregator import BaseAggregator
from aggregator.aggregator_registry import AggregatorRegistry
from aggregator.aggregator_executor import AggregatorExecutor
from aggregator.aggregator_agent import AggregatorAgent

# 3. MCP components
from mcp.tool_registry import MCPToolRegistry
from mcp.tool_executor import MCPToolExecutor
from mcp.server import MCPServer
from mcp.mcp_tools import AnalyzeCalligraphyTool

def test_full_mcp_pipeline_integration():
    ctx = ContextManager()
    agent_registry = AgentRegistry()
    
    # 1. Knowledge
    class DummyKnowledge(BaseKnowledge):
        @property
        def knowledge_name(self) -> str: return "dummy_knowledge"
        def lookup(self, query: str) -> Any: return f"Knowledge of {query}"
    know_reg = KnowledgeRegistry()
    know_reg.register(DummyKnowledge())
    agent_registry.register(KnowledgeAgent(know_reg, KnowledgeExecutor(), ctx))
    
    # 2. Reasoner
    class DummyReasoner(BaseReasoner):
        @property
        def reasoner_name(self) -> str: return "dummy_reasoner"
        def reason(self, request: str, memory_context: Any) -> Dict[str, Any]: return {"selected_route": "smart_mega_route"}
    reasoner_registry = ReasonerRegistry()
    reasoner_registry.register(DummyReasoner())
    agent_registry.register(ReasoningAgent(reasoner_registry, ReasoningExecutor(ctx), ctx))
    
    # 3. Router & 4. Planner
    class MegaPlanA(BasePlan):
        @property
        def plan_name(self) -> str: return "mega_plan_a"
        def build(self, request: str) -> List[str]: return ["prompt_agent", "extractor", "tool_agent"]
    plan_registry = PlannerRegistry()
    plan_registry.register(MegaPlanA())
    planner_executor = PlannerExecutor(agent_registry, ctx)
    
    class SmartMegaRoute(BaseRoute):
        @property
        def route_name(self) -> str: return "smart_mega_route"
        def select(self, request: str) -> str: return "mega_plan_a"
    route_registry = RouteRegistry()
    route_registry.register(SmartMegaRoute())
    agent_registry.register(RouterAgent(route_registry, RouteExecutor(plan_registry, planner_executor), ctx))
    
    # 5. Prompt & 6. Extractor & 7. Tool
    prompt_reg = PromptRegistry()
    prompt_reg.register(PromptTemplate("mega_prompt", "Prompt Output: {info}"))
    agent_registry.register(PromptAgent(prompt_reg, ctx))
    
    class ExtractAgent(BaseAgent):
        @property
        def agent_name(self) -> str: return "extractor"
        def process(self, request: str) -> str: return json.dumps({"tool_name": "sim_tool", "args": {}})
    agent_registry.register(ExtractAgent())
    
    class SimpleTool(BaseTool):
        @property
        def tool_name(self) -> str: return "sim_tool"
        def execute(self, **kwargs): return "Mega Tool Success"
    tool_reg = ToolRegistry()
    tool_reg.register(SimpleTool())
    agent_registry.register(ToolAgent(tool_reg, ctx))

    # 8. Conversation
    class MockConv(BaseConversation):
        @property
        def conversation_name(self) -> str: return "dummy_conversation"
        def respond(self, message: str, history: list) -> Any: return f"Response: {message}"
    conv_registry = ConversationRegistry()
    conv_registry.register(MockConv())
    class LocalMockContextManager:
        def get_recent_history(self): return []
    local_ctx = LocalMockContextManager()
    agent_registry.register(ConversationAgent(conv_registry, ConversationExecutor(local_ctx), local_ctx))
    
    # 9. Reflection
    class DummyReflection(BaseReflection):
        @property
        def reflection_name(self) -> str: return "dummy_reflection"
        def analyze(self, input_data: Any) -> Any: return {"quality": "good", "summary": str(input_data)}
    ref_registry = ReflectionRegistry()
    ref_registry.register(DummyReflection())
    agent_registry.register(ReflectionAgent(ref_registry, ReflectionExecutor(), ctx))
    
    # 10. Critic
    class DummyCritic(BaseCritic):
        @property
        def critic_name(self) -> str: return "dummy_critic"
        def evaluate(self, candidate: Any) -> Any: return {"score": 9.5, "feedback": f"Critique of {candidate}"}
    crit_registry = CriticRegistry()
    crit_registry.register(DummyCritic())
    agent_registry.register(CriticAgent(crit_registry, CriticExecutor(), ctx))
    
    # 11. Memory Store
    class DummyMemoryStore(BaseMemoryStore):
        def __init__(self): self._db = {}
        @property
        def memory_store_name(self) -> str: return "dummy_store"
        def save(self, key: str, value: Any) -> None: self._db[key] = value
        def load(self, key: str) -> Any: return self._db.get(key)
    store_registry = MemoryStoreRegistry()
    store_registry.register(DummyMemoryStore())
    agent_registry.register(MemoryStoreAgent(store_registry, MemoryStoreExecutor(), ctx))
    
    # 12. Evaluator
    class DummyEvaluator(BaseEvaluator):
        @property
        def evaluator_name(self) -> str: return "dummy_evaluator"
        def evaluate(self, candidate: Any) -> Any: return {"grade": "A", "confidence": 0.98, "summary": f"Evaluation of {candidate}"}
    eval_registry = EvaluatorRegistry()
    eval_registry.register(DummyEvaluator())
    agent_registry.register(EvaluatorAgent(eval_registry, EvaluatorExecutor(), ctx))
    
    # 13. Validator
    class DummyValidator(BaseValidator):
        @property
        def validator_name(self) -> str: return "dummy_validator"
        def validate(self, candidate: Any) -> Any: return {"valid": True, "confidence": 0.99, "summary": f"Validated {candidate}"}
    val_registry = ValidatorRegistry()
    val_registry.register(DummyValidator())
    agent_registry.register(ValidatorAgent(val_registry, ValidatorExecutor(), ctx))
    
    # 14. Scorer
    class DummyScorer(BaseScorer):
        @property
        def scorer_name(self) -> str: return "dummy_scorer"
        def score(self, candidate: Any) -> Any: return {"score": 9.8, "confidence": 0.99, "reason": f"Scored {candidate}"}
    scorer_registry = ScorerRegistry()
    scorer_registry.register(DummyScorer())
    agent_registry.register(ScorerAgent(scorer_registry, ScorerExecutor(), ctx))
    
    # 15. Ranker
    class DummyRanker(BaseRanker):
        @property
        def ranker_name(self) -> str: return "dummy_ranker"
        def rank(self, candidates: Any) -> Any: return {"winner": candidates[0] if isinstance(candidates, list) else candidates, "rank": 1}
    ranker_registry = RankerRegistry()
    ranker_registry.register(DummyRanker())
    agent_registry.register(RankerAgent(ranker_registry, RankerExecutor(), ctx))
    
    # 16. Selector
    class DummySelector(BaseSelector):
        @property
        def selector_name(self) -> str: return "dummy_selector"
        def select(self, candidates: Any) -> Any: return {"selected": candidates[0] if isinstance(candidates, list) else candidates, "confidence": 0.99}
    selector_registry = SelectorRegistry()
    selector_registry.register(DummySelector())
    agent_registry.register(SelectorAgent(selector_registry, SelectorExecutor(), ctx))

    # 17. Aggregator
    class DummyAggregator(BaseAggregator):
        @property
        def aggregator_name(self) -> str: return "dummy_aggregator"
        def aggregate(self, items: Any) -> Any: return {"combined": items, "summary": "Aggregated final results"}
    aggregator_registry = AggregatorRegistry()
    aggregator_registry.register(DummyAggregator())
    agent_registry.register(AggregatorAgent(aggregator_registry, AggregatorExecutor(), ctx))
    
    # ---- ORCHESTRATOR ----
    orchestrator = AgentOrchestrator(agent_registry, ctx)
    
    # ---- MCP INTEGRATION ----
    mcp_registry = MCPToolRegistry()
    analyze_tool = AnalyzeCalligraphyTool(orchestrator=orchestrator)
    mcp_registry.register(analyze_tool)
    
    mcp_executor = MCPToolExecutor(mcp_registry)
    mcp_server = MCPServer(mcp_executor)
    
    # TRIGGER FULL PIPELINE VIA MCP
    mcp_req = json.dumps({
        "tool": "analyze_calligraphy",
        "arguments": {
            "data": "gothic script"
        }
    })
    
    mcp_response_str = mcp_server.handle_request(mcp_req)
    mcp_response = json.loads(mcp_response_str)
    
    assert mcp_response["status"] == "success"
    assert mcp_response["tool"] == "analyze_calligraphy"
    
    final_result = mcp_response["result"]
    assert "Aggregated final results" in final_result["summary"]
    
    # Traverse down to prove it went all the way through Knowledge -> Reasoner -> Router ... -> Selector
    selected_winner = final_result["combined"][0]["selected"]["winner"]
    assert selected_winner["score"] == 9.8
    assert "Evaluation of" in selected_winner["reason"]

def test_full_mcp_pipeline_failure_handling():
    ctx = ContextManager()
    agent_registry = AgentRegistry()
    
    # Register only Knowledge with a crash
    class FailingKnowledge(BaseKnowledge):
        @property
        def knowledge_name(self) -> str: return "dummy_knowledge"
        def lookup(self, query: str) -> Any: raise ValueError("Intentional database corruption")
    
    know_reg = KnowledgeRegistry()
    know_reg.register(FailingKnowledge())
    agent_registry.register(KnowledgeAgent(know_reg, KnowledgeExecutor(), ctx))
    
    orchestrator = AgentOrchestrator(agent_registry, ctx)
    mcp_registry = MCPToolRegistry()
    mcp_registry.register(AnalyzeCalligraphyTool(orchestrator=orchestrator))
    mcp_executor = MCPToolExecutor(mcp_registry)
    mcp_server = MCPServer(mcp_executor)
    
    mcp_req = json.dumps({
        "tool": "analyze_calligraphy",
        "arguments": {
            "data": "gothic script"
        }
    })
    
    mcp_response_str = mcp_server.handle_request(mcp_req)
    mcp_response = json.loads(mcp_response_str)
    
    assert mcp_response["status"] == "success"
    assert mcp_response["tool"] == "analyze_calligraphy"
    assert "error" in mcp_response["result"]
    assert "Pipeline failed at knowledge_agent" in mcp_response["result"]["error"]

def test_mcp_invalid_payload_format():
    mcp_registry = MCPToolRegistry()
    mcp_executor = MCPToolExecutor(mcp_registry)
    mcp_server = MCPServer(mcp_executor)
    
    # Send a JSON array instead of dictionary
    mcp_req = json.dumps(["invalid", "array", "payload"])
    
    mcp_response_str = mcp_server.handle_request(mcp_req)
    mcp_response = json.loads(mcp_response_str)
    
    assert mcp_response.get("error") == "Invalid request format. Expected JSON dictionary."
