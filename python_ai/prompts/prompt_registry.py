from typing import Dict, Optional, List
from .base_prompt import BasePrompt

class PromptRegistry:
    """Localized catalog of available prompt templates."""
    
    def __init__(self):
        self._prompts: Dict[str, BasePrompt] = {}

    def register(self, prompt: BasePrompt) -> None:
        """Registers a prompt template by its prompt_name."""
        self._prompts[prompt.prompt_name] = prompt

    def get(self, name: str) -> Optional[BasePrompt]:
        """Retrieves a registered prompt or safely returns None."""
        return self._prompts.get(name)

    def list_prompts(self) -> List[str]:
        """Returns the keys of all registered prompts."""
        return list(self._prompts.keys())
