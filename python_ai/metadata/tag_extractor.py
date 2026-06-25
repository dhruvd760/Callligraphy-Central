import logging
from response_models import TagResult
from defaults import TAG_DEFAULT
from prompts.metadata_prompts import SYSTEM_INSTRUCTION, PROMPT_TAGS
from .base_component import BaseMetadataComponent

logger = logging.getLogger(__name__)

class TagExtractor(BaseMetadataComponent):
    """
    Component responsible for extracting searchable tags.
    """
    def extract(self, text: str) -> TagResult:
        prompt = PROMPT_TAGS.replace('{text}', text)
        result = self.executor.execute_task(SYSTEM_INSTRUCTION, prompt)
        
        if result and isinstance(result, list):
            return TagResult(tags=result)
        
        return TAG_DEFAULT
