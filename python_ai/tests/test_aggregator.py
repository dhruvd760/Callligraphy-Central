import pytest
import sys
import os
import json
from typing import List, Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from aggregator.base_aggregator import BaseAggregator
from aggregator.aggregator_registry import AggregatorRegistry
from aggregator.aggregator_executor import AggregatorExecutor
from aggregator.aggregator_agent import AggregatorAgent

from selector.base_selector import BaseSelector
from selector.selector_registry import SelectorRegistry
from selector.selector_executor import SelectorExecutor
from selector.selector_agent import SelectorAgent

from ranker.base_ranker import BaseRanker
from ranker.ranker_registry import RankerRegistry
from ranker.ranker_executor import RankerExecutor
from ranker.ranker_agent import RankerAgent

from scorer.base_scorer import BaseScorer
from scorer.scorer_registry import ScorerRegistry
from scorer.scorer_executor import ScorerExecutor
from scorer.scorer_agent import ScorerAgent

from validator.base_validator import BaseValidator
from validator.validator_registry import ValidatorRegistry
from validator.validator_executor import ValidatorExecutor
from validator.validator_agent import ValidatorAgent

from evaluator.base_evaluator import BaseEvaluator
from evaluator.evaluator_registry import EvaluatorRegistry
from evaluator.evaluator_executor import EvaluatorExecutor
from evaluator.evaluator_agent import EvaluatorAgent

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
class DummyAggregator(BaseAggregator):
    @property
    def aggregator_name(self) -> str:
        return "dummy_aggregator"

    def aggregate(self, items: Any) -> Any:
        if items == "crash":
            raise ValueError("Intentional aggregator crash")

        return {
            "combined": items,
            "count": len(items) if isinstance(items, list) else 1,
            "summary": "Aggregated results"
        }

def test_base_aggregator_contract():
    class InvalidAggregator(BaseAggregator):
        pass
    with pytest.raises(TypeError):
        InvalidAggregator()

def test_aggregator_registry():
    registry = AggregatorRegistry()
    aggregator = DummyAggregator()
    
    registry.register(aggregator)
    assert registry.list_aggregators() == ["dummy_aggregator"]
    
    assert registry.get("dummy_aggregator") is aggregator
    assert registry.get("missing") is None

def test_aggregator_executor():
    executor = AggregatorExecutor()
    aggregator = DummyAggregator()
    
    # Valid
    res = executor.execute_aggregate(["test data 1", "test data 2"], aggregator)
    assert res["aggregate_result"]["count"] == 2
    assert res["aggregate_result"]["summary"] == "Aggregated results"
    assert res["aggregate_result"]["combined"] == ["test data 1", "test data 2"]

def test_executor_exception_handling():
    executor = AggregatorExecutor()
    aggregator = DummyAggregator()
    
    # Error
    res_err = executor.execute_aggregate("crash", aggregator)
    assert "error" in res_err
    assert "Intentional aggregator crash" in res_err["error"]

def test_aggregator_agent():
    registry = AggregatorRegistry()
    registry.register(DummyAggregator())
    
    executor = AggregatorExecutor()
    ctx = ContextManager()
    agent = AggregatorAgent(registry, executor, ctx)
    
    # Valid
    req = json.dumps({"aggregator_name": "dummy_aggregator", "items": ["test candidate"]})
    res = agent.process(req)
    assert res["status"] == "success"
    assert res["aggregator"] == "dummy_aggregator"
    assert res["result"]["count"] == 1
    assert res["result"]["summary"] == "Aggregated results"
    assert res["result"]["combined"] == ["test candidate"]

def test_missing_aggregator():
    registry = AggregatorRegistry()
    executor = AggregatorExecutor()
    ctx = ContextManager()
    agent = AggregatorAgent(registry, executor, ctx)
    
    res_miss = agent.process(json.dumps({"aggregator_name": "missing", "items": ["c"]}))
    assert res_miss == {"error": "Aggregator source 'missing' not found."}

def test_missing_aggregator_name():
    registry = AggregatorRegistry()
    executor = AggregatorExecutor()
    ctx = ContextManager()
    agent = AggregatorAgent(registry, executor, ctx)
    
    res_no_name = agent.process("{}")
    assert res_no_name == {"error": "No 'aggregator_name' provided in request."}

def test_invalid_json():
    registry = AggregatorRegistry()
    executor = AggregatorExecutor()
    ctx = ContextManager()
    agent = AggregatorAgent(registry, executor, ctx)
    
    res_inv = agent.process("not json")
    assert res_inv == {"error": "Invalid aggregator request format. Expected JSON."}

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
    class DummyMemoryStore(BaseMemoryStore):
        def __init__(self):
            self._db = {}
        @property
        def memory_store_name(self) -> str:
            return "dummy_store"
        def save(self, key: str, value: Any) -> None:
            self._db[key] = value
        def load(self, key: str) -> Any:
            return self._db.get(key)
            
    store_registry = MemoryStoreRegistry()
    store_registry.register(DummyMemoryStore())
    store_executor = MemoryStoreExecutor()
    store_agent = MemoryStoreAgent(store_registry, store_executor, ctx)
    agent_registry.register(store_agent)
    
    # 14. Evaluator
    class DummyEvaluator(BaseEvaluator):
        @property
        def evaluator_name(self) -> str:
            return "dummy_evaluator"
        def evaluate(self, candidate: Any) -> Any:
            return {"grade": "A", "confidence": 0.98, "summary": f"Evaluation of {candidate}"}

    eval_registry = EvaluatorRegistry()
    eval_registry.register(DummyEvaluator())
    eval_executor = EvaluatorExecutor()
    eval_agent = EvaluatorAgent(eval_registry, eval_executor, ctx)
    agent_registry.register(eval_agent)
    
    # 15. Validator
    class DummyValidator(BaseValidator):
        @property
        def validator_name(self) -> str:
            return "dummy_validator"
        def validate(self, candidate: Any) -> Any:
            return {"valid": True, "confidence": 0.99, "summary": f"Validated {candidate}"}

    val_registry = ValidatorRegistry()
    val_registry.register(DummyValidator())
    val_executor = ValidatorExecutor()
    val_agent = ValidatorAgent(val_registry, val_executor, ctx)
    agent_registry.register(val_agent)
    
    # 16. Scorer
    class DummyScorer(BaseScorer):
        @property
        def scorer_name(self) -> str:
            return "dummy_scorer"
        def score(self, candidate: Any) -> Any:
            return {"score": 9.8, "confidence": 0.99, "reason": f"Scored {candidate}"}

    scorer_registry = ScorerRegistry()
    scorer_registry.register(DummyScorer())
    scorer_executor = ScorerExecutor()
    scorer_agent = ScorerAgent(scorer_registry, scorer_executor, ctx)
    agent_registry.register(scorer_agent)
    
    # 17. Ranker
    class DummyRanker(BaseRanker):
        @property
        def ranker_name(self) -> str:
            return "dummy_ranker"
        def rank(self, candidates: Any) -> Any:
            return {"winner": candidates[0] if isinstance(candidates, list) else candidates, "rank": 1, "confidence": 0.99, "reason": "Highest score candidate"}

    ranker_registry = RankerRegistry()
    ranker_registry.register(DummyRanker())
    ranker_executor = RankerExecutor()
    ranker_agent = RankerAgent(ranker_registry, ranker_executor, ctx)
    agent_registry.register(ranker_agent)
    
    # 18. Selector
    class DummySelector(BaseSelector):
        @property
        def selector_name(self) -> str:
            return "dummy_selector"
        def select(self, candidates: Any) -> Any:
            return {"selected": candidates[0] if isinstance(candidates, list) else candidates, "confidence": 0.99, "reason": "Best overall candidate"}

    selector_registry = SelectorRegistry()
    selector_registry.register(DummySelector())
    selector_executor = SelectorExecutor()
    selector_agent = SelectorAgent(selector_registry, selector_executor, ctx)
    agent_registry.register(selector_agent)

    # 19. Aggregator
    aggregator_registry = AggregatorRegistry()
    aggregator_registry.register(DummyAggregator())
    aggregator_executor = AggregatorExecutor()
    aggregator_agent = AggregatorAgent(aggregator_registry, aggregator_executor, ctx)
    agent_registry.register(aggregator_agent)
    
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
    orchestrator.execute_sequential(store_req, ["memory_store_agent"])
    
    store_load_req = json.dumps({
        "memory_store_name": "dummy_store",
        "operation": "load",
        "key": "final_critique_result"
    })
    res_load = orchestrator.execute_sequential(store_load_req, ["memory_store_agent"])
    loaded_val = res_load["memory_store_agent"]["result"]["value"]
    
    # Step H: Evaluator
    eval_req = json.dumps({
        "evaluator_name": "dummy_evaluator",
        "candidate": loaded_val
    })
    res_eval = orchestrator.execute_sequential(eval_req, ["evaluator_agent"])
    eval_output = res_eval["evaluator_agent"]["result"]
    
    # Step I: Validator
    val_req = json.dumps({
        "validator_name": "dummy_validator",
        "candidate": eval_output
    })
    res_val = orchestrator.execute_sequential(val_req, ["validator_agent"])
    val_output = res_val["validator_agent"]["result"]
    
    # Step J: Scorer
    score_req = json.dumps({
        "scorer_name": "dummy_scorer",
        "candidate": val_output
    })
    res_score = orchestrator.execute_sequential(score_req, ["scorer_agent"])
    score_output = res_score["scorer_agent"]["result"]
    
    # Step K: Ranker
    rank_req = json.dumps({
        "ranker_name": "dummy_ranker",
        "candidates": [score_output]
    })
    res_rank = orchestrator.execute_sequential(rank_req, ["ranker_agent"])
    rank_output = res_rank["ranker_agent"]["result"]
    
    # Step L: Selector
    sel_req = json.dumps({
        "selector_name": "dummy_selector",
        "candidates": [rank_output]
    })
    res_sel = orchestrator.execute_sequential(sel_req, ["selector_agent"])
    selector_output = res_sel["selector_agent"]["result"]

    # Step M: Aggregator
    agg_req = json.dumps({
        "aggregator_name": "dummy_aggregator",
        "items": [selector_output]
    })
    res_agg = orchestrator.execute_sequential(agg_req, ["aggregator_agent"])
    
    # Final assertions
    assert res_agg["aggregator_agent"]["status"] == "success"
    assert res_agg["aggregator_agent"]["result"]["count"] == 1
    assert "Aggregated results" in res_agg["aggregator_agent"]["result"]["summary"]
