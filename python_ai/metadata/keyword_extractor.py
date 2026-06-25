import logging
from response_models import KeywordResult
from defaults import KEYWORD_DEFAULT
from prompts.metadata_prompts import SYSTEM_INSTRUCTION, PROMPT_KEYWORDS
from .base_component import BaseMetadataComponent

logger = logging.getLogger(__name__)

class KeywordExtractor(BaseMetadataComponent):
    """
    Component responsible for extracting educational and technical keywords.
    """
    def extract(self, text: str) -> KeywordResult:
        prompt = PROMPT_KEYWORDS.replace('{text}', text)
        result = self.executor.execute_task(SYSTEM_INSTRUCTION, prompt)
        
        if result and isinstance(result, list):
            return KeywordResult(keywords=result)
        
        return KEYWORD_DEFAULT
