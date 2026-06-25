import json
from typing import Any
from .base_tool import BaseMCPTool

class AnalyzeCalligraphyTool(BaseMCPTool):
    """MCP Tool to analyze calligraphy samples."""
    
    @property
    def tool_name(self) -> str:
        return "analyze_calligraphy"
        
    def execute(self, **kwargs: Any) -> Any:
        if not self.orchestrator:
            return {
                "status": "success",
                "tool": "analyze_calligraphy",
                "result": "Dummy analysis."
            }
            
        def extract(res: dict, agent_name: str) -> Any:
            ag_res = res.get(agent_name, {})
            if isinstance(ag_res, dict) and "error" in ag_res:
                raise RuntimeError(f"Pipeline failed at {agent_name}: {ag_res['error']}")
            return ag_res.get("result", ag_res) if isinstance(ag_res, dict) else ag_res

        try:
            # 1. Knowledge
            req1 = json.dumps({"knowledge_name": "dummy_knowledge", "query": kwargs.get("data", "calligraphy")})
            res1 = self.orchestrator.execute_sequential(req1, ["knowledge_agent"])
            ag1 = extract(res1, "knowledge_agent")
            info = ag1.get("result", ag1) if isinstance(ag1, dict) else ag1
            
            # 2. Reasoner
            req2 = json.dumps({"reasoner_name": "dummy_reasoner", "request": "think"})
            res2 = self.orchestrator.execute_sequential(req2, ["reasoning_agent"])
            ag2 = extract(res2, "reasoning_agent")
            route_name = ag2.get("selected_route", "smart_mega_route") if isinstance(ag2, dict) else "smart_mega_route"
            
            # 3,4,5,6,7. Router -> Planner -> Prompt -> Extractor -> Tool
            router_req = json.dumps({
                "route_name": route_name,
                "request": json.dumps({"prompt_name": "mega_prompt", "args": {"info": info}})
            })
            res_orch = self.orchestrator.execute_sequential(router_req, ["router_agent"])
            ag_orch = extract(res_orch, "router_agent")
            router_output = ag_orch.get("result", str(ag_orch)) if isinstance(ag_orch, dict) else str(ag_orch)
            
            # 8. Conversation
            conv_req = json.dumps({
                "conversation_name": "dummy_conversation", 
                "message": f"Tool says: {router_output}"
            })
            res_conv = self.orchestrator.execute_sequential(conv_req, ["conversation_agent"])
            ag_conv = extract(res_conv, "conversation_agent")
            conv_output = ag_conv.get("response", str(ag_conv)) if isinstance(ag_conv, dict) else str(ag_conv)
            
            # 9. Reflection
            ref_req = json.dumps({
                "reflection_name": "dummy_reflection",
                "input": conv_output
            })
            res_ref = self.orchestrator.execute_sequential(ref_req, ["reflection_agent"])
            ref_output = extract(res_ref, "reflection_agent")
            
            # 10. Critic
            crit_req = json.dumps({
                "critic_name": "dummy_critic",
                "candidate": ref_output
            })
            res_crit = self.orchestrator.execute_sequential(crit_req, ["critic_agent"])
            crit_output = extract(res_crit, "critic_agent")
            
            # 11. Memory Store
            store_req = json.dumps({
                "memory_store_name": "dummy_store",
                "operation": "save",
                "key": "mcp_pipeline_result",
                "value": crit_output
            })
            self.orchestrator.execute_sequential(store_req, ["memory_store_agent"])
            
            store_load_req = json.dumps({
                "memory_store_name": "dummy_store",
                "operation": "load",
                "key": "mcp_pipeline_result"
            })
            res_load = self.orchestrator.execute_sequential(store_load_req, ["memory_store_agent"])
            ag_load = extract(res_load, "memory_store_agent")
            loaded_val = ag_load.get("value", ag_load) if isinstance(ag_load, dict) else ag_load
            
            # 12. Evaluator
            eval_req = json.dumps({
                "evaluator_name": "dummy_evaluator",
                "candidate": loaded_val
            })
            res_eval = self.orchestrator.execute_sequential(eval_req, ["evaluator_agent"])
            eval_output = extract(res_eval, "evaluator_agent")
            
            # 13. Validator
            val_req = json.dumps({
                "validator_name": "dummy_validator",
                "candidate": eval_output
            })
            res_val = self.orchestrator.execute_sequential(val_req, ["validator_agent"])
            val_output = extract(res_val, "validator_agent")
            
            # 14. Scorer
            score_req = json.dumps({
                "scorer_name": "dummy_scorer",
                "candidate": val_output
            })
            res_score = self.orchestrator.execute_sequential(score_req, ["scorer_agent"])
            score_output = extract(res_score, "scorer_agent")
            
            # 15. Ranker
            rank_req = json.dumps({
                "ranker_name": "dummy_ranker",
                "candidates": [score_output]
            })
            res_rank = self.orchestrator.execute_sequential(rank_req, ["ranker_agent"])
            rank_output = extract(res_rank, "ranker_agent")
            
            # 16. Selector
            sel_req = json.dumps({
                "selector_name": "dummy_selector",
                "candidates": [rank_output]
            })
            res_sel = self.orchestrator.execute_sequential(sel_req, ["selector_agent"])
            selector_output = extract(res_sel, "selector_agent")

            # 17. Aggregator
            agg_req = json.dumps({
                "aggregator_name": "dummy_aggregator",
                "items": [selector_output]
            })
            res_agg = self.orchestrator.execute_sequential(agg_req, ["aggregator_agent"])
            
            return extract(res_agg, "aggregator_agent")
            
        except RuntimeError as e:
            return {"error": str(e)}


class GeneratePracticeSheetTool(BaseMCPTool):
    """MCP Tool to generate practice sheets."""
    
    @property
    def tool_name(self) -> str:
        return "generate_practice_sheet"
        
    def execute(self, **kwargs: Any) -> Any:
        return "Dummy practice sheet generation."


class EvaluateSubmissionTool(BaseMCPTool):
    """MCP Tool to evaluate student submissions."""
    
    @property
    def tool_name(self) -> str:
        return "evaluate_submission"
        
    def execute(self, **kwargs: Any) -> Any:
        return "Dummy evaluation."


class SearchStylesTool(BaseMCPTool):
    """MCP Tool to search calligraphy styles."""
    
    @property
    def tool_name(self) -> str:
        return "search_styles"
        
    def execute(self, **kwargs: Any) -> Any:
        return "Dummy search results."


class SaveSessionTool(BaseMCPTool):
    """MCP Tool to save a tutoring session."""
    
    @property
    def tool_name(self) -> str:
        return "save_session"
        
    def execute(self, **kwargs: Any) -> Any:
        return "Dummy session saved."


class LoadSessionTool(BaseMCPTool):
    """MCP Tool to load a previous session."""
    
    @property
    def tool_name(self) -> str:
        return "load_session"
        
    def execute(self, **kwargs: Any) -> Any:
        return "Dummy session loaded."
