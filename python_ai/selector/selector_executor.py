from typing import Any
from .base_selector import BaseSelector

class SelectorExecutor:
    """Executes selection securely against candidates."""
    
    def execute_select(self, candidates: Any, selector: BaseSelector) -> Any:
        try:
            result = selector.select(candidates)
            return {"select_result": result}
        except Exception as e:
            return {"error": f"Selector execution failed for '{selector.selector_name}': {str(e)}"}
