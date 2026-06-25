import logging
from response_models import StyleResult
from defaults import STYLE_DEFAULT
from prompts.metadata_prompts import SYSTEM_INSTRUCTION, PROMPT_STYLE
from .base_component import BaseMetadataComponent

logger = logging.getLogger(__name__)

class StyleClassifier(BaseMetadataComponent):
    """
    Component responsible for identifying the calligraphy style.
    """
    def extract(self, text: str) -> StyleResult:
        prompt = PROMPT_STYLE.replace('{text}', text)
        result = self.executor.execute_task(SYSTEM_INSTRUCTION, prompt)
        
        if result and isinstance(result, dict):
            return StyleResult(
                style=result.get("style", STYLE_DEFAULT.style),
                confidence=result.get("confidence", STYLE_DEFAULT.confidence),
                reason=result.get("reason", STYLE_DEFAULT.reason)
            )
        
        return STYLE_DEFAULT
