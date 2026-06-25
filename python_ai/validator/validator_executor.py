from typing import Any
from .base_validator import BaseValidator

class ValidatorExecutor:
    """Executes a validation securely against a candidate block."""
    
    def execute_validation(self, candidate: Any, validator: BaseValidator) -> Any:
        try:
            result = validator.validate(candidate)
            return {"validation": result}
        except Exception as e:
            return {"error": f"Validator execution failed for '{validator.validator_name}': {str(e)}"}
