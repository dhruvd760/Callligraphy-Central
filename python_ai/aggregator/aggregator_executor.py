from typing import Any
from .base_aggregator import BaseAggregator

class AggregatorExecutor:
    """Executes aggregation securely against items."""
    
    def execute_aggregate(self, items: Any, aggregator: BaseAggregator) -> Any:
        try:
            result = aggregator.aggregate(items)
            return {"aggregate_result": result}
        except Exception as e:
            return {"error": f"Aggregator execution failed for '{aggregator.aggregator_name}': {str(e)}"}
