import logging
from response_models import LanguageResult
from defaults import LANGUAGE_DEFAULT
from prompts.metadata_prompts import SYSTEM_INSTRUCTION, PROMPT_LANGUAGE
from .base_component import BaseMetadataComponent

logger = logging.getLogger(__name__)

class LanguageDetector(BaseMetadataComponent):
    """
    Component responsible for detecting the language of the calligraphy text.
    """
    def extract(self, text: str) -> LanguageResult:
        prompt = PROMPT_LANGUAGE.replace('{text}', text)
        result = self.executor.execute_task(SYSTEM_INSTRUCTION, prompt)
        
        if result and isinstance(result, dict) and "language" in result:
            return LanguageResult(language=result.get("language"))
        
        return LANGUAGE_DEFAULT
