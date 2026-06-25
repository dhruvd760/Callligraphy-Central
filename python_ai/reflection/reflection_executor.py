from typing import Any
from .base_reflection import BaseReflection

class ReflectionExecutor:
    """Executes a reflection analysis against a selected reflection block."""
    
    def execute_reflection(self, input_data: Any, reflection: BaseReflection) -> Any:
        try:
            result = reflection.analyze(input_data)
            return {"reflection": result}
        except Exception as e:
            return {"error": f"Reflection execution failed for '{reflection.reflection_name}': {str(e)}"}
