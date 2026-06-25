import logging
from response_models import TitleResult
from defaults import TITLE_DEFAULT
from prompts.metadata_prompts import SYSTEM_INSTRUCTION, PROMPT_TITLE
from .base_component import BaseMetadataComponent

logger = logging.getLogger(__name__)

class TitleGenerator(BaseMetadataComponent):
    """
    Component responsible for generating a suitable title.
    """
    def extract(self, text: str) -> TitleResult:
        prompt = PROMPT_TITLE.replace('{text}', text)
        result = self.executor.execute_task(SYSTEM_INSTRUCTION, prompt)
        
        if result and isinstance(result, dict) and "title" in result:
            return TitleResult(title=result.get("title"))
        
        return TITLE_DEFAULT
