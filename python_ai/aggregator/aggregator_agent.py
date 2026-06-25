import json
import sys
import os
from typing import Optional, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agents.base_agent import BaseAgent
from memory.context_manager import ContextManager
from .aggregator_registry import AggregatorRegistry
from .aggregator_executor import AggregatorExecutor

class AggregatorAgent(BaseAgent):
    """
    A specialized BaseAgent capable of processing aggregations securely.
    """
    def __init__(self, aggregator_registry: AggregatorRegistry, aggregator_executor: AggregatorExecutor, context_manager: Optional[ContextManager] = None):
        super().__init__(context_manager)
        self.aggregator_registry = aggregator_registry
        self.aggregator_executor = aggregator_executor

    @property
    def agent_name(self) -> str:
        return "aggregator_agent"

    def process(self, request: str) -> Any:
        try:
            parsed = self.parse_request(request)
            aggregator_name = parsed.get("aggregator_name")
            items = parsed.get("items")

            if not aggregator_name:
                return {"error": "No 'aggregator_name' provided in request."}

            aggregator = self.aggregator_registry.get(aggregator_name)
            if aggregator is None:
                return {"error": f"Aggregator source '{aggregator_name}' not found."}

            exec_res = self.aggregator_executor.execute_aggregate(items, aggregator)
            
            if isinstance(exec_res, dict) and "error" in exec_res:
                return exec_res
                
            return {
                "status": "success",
                "aggregator": aggregator_name,
                "result": exec_res.get("aggregate_result")
            }

        except json.JSONDecodeError:
            return {"error": "Invalid aggregator request format. Expected JSON."}
        except Exception as e:
            return {"error": str(e)}
