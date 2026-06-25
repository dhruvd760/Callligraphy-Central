from .base_prompt import BasePrompt

class PromptTemplate(BasePrompt):
    """Concrete implementation of a prompt template using Python string formatting."""
    
    def __init__(self, prompt_name: str, template: str):
        self._prompt_name = prompt_name
        self._template = template

    @property
    def prompt_name(self) -> str:
        return self._prompt_name

    def render(self, **kwargs) -> str:
        return self._template.format(**kwargs)
