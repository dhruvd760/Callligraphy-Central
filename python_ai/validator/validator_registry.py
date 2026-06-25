from typing import Dict, Optional, List
from .base_validator import BaseValidator

class ValidatorRegistry:
    """Localized catalog of available validator components."""
    
    def __init__(self):
        self._validators: Dict[str, BaseValidator] = {}

    def register(self, validator: BaseValidator) -> None:
        """Registers a validator by its validator_name."""
        self._validators[validator.validator_name] = validator

    def get(self, name: str) -> Optional[BaseValidator]:
        """Retrieves a registered validator safely returning None if missing."""
        return self._validators.get(name)

    def list_validators(self) -> List[str]:
        """Returns the keys of all registered validator blocks."""
        return list(self._validators.keys())
