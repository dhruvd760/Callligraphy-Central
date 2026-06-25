import json
import sys
import os
from typing import Optional, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.base_agent import BaseAgent
from memory.context_manager import ContextManager
from .prompt_registry import PromptRegistry

class PromptAgent(BaseAgent):
    """
    A specialized BaseAgent capable of parsing requests and securely rendering
    prompt templates through the PromptRegistry.
    """
    def __init__(self, prompt_registry: PromptRegistry, context_manager: Optional[ContextManager] = None):
        super().__init__(context_manager)
        self.prompt_registry = prompt_registry

    @property
    def agent_name(self) -> str:
        return "prompt_agent"

    def process(self, request: str) -> Any:
        try:
            parsed = self.parse_request(request)
            prompt_name = parsed.get("prompt_name")
            kwargs = parsed.get("args", {})

            if not prompt_name:
                return {"error": "No 'prompt_name' provided in request."}

            prompt = self.prompt_registry.get(prompt_name)
            if prompt is None:
                return {"error": f"Prompt '{prompt_name}' not found."}

            rendered = prompt.render(**kwargs)
            return {
                "status": "success",
                "prompt": prompt_name,
                "rendered": rendered
            }

        except json.JSONDecodeError:
            return {"error": "Invalid prompt request format. Expected JSON."}
        except KeyError as e:
            return {"error": f"Missing formatting argument: {e}"}
        except Exception as e:
            return {"error": str(e)}
