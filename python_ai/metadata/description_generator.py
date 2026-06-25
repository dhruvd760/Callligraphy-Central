import logging
from response_models import DescriptionResult
from defaults import DESCRIPTION_DEFAULT
from prompts.metadata_prompts import SYSTEM_INSTRUCTION, PROMPT_DESCRIPTION
from .base_component import BaseMetadataComponent

logger = logging.getLogger(__name__)

class DescriptionGenerator(BaseMetadataComponent):
    """
    Component responsible for producing a beginner-friendly description.
    """
    def extract(self, text: str) -> DescriptionResult:
        prompt = PROMPT_DESCRIPTION.replace('{text}', text)
        result = self.executor.execute_task(SYSTEM_INSTRUCTION, prompt)
        
        if result and isinstance(result, dict) and "description" in result:
            return DescriptionResult(description=result.get("description"))
        
        return DESCRIPTION_DEFAULT
