import logging
import dataclasses
from typing import Dict, Any, List

from gemini_client import GeminiClient
from utils.gemini_task_executor import GeminiTaskExecutor
from response_models import MetadataResult
from metadata import (
    TagExtractor,
    KeywordExtractor,
    StyleClassifier,
    LanguageDetector,
    DescriptionGenerator,
    TitleGenerator
)

logger = logging.getLogger(__name__)

class MetadataAgent:
    """
    Orchestrator for metadata generation.
    Delegates all business logic and Gemini interaction to single-responsibility components.
    """

    def __init__(self) -> None:
        """
        Initializes the shared Gemini client and execution components.
        """
        logger.info("Initializing MetadataAgent...")
        try:
            self.gemini_client = GeminiClient()
            logger.info("GeminiClient successfully initialized in MetadataAgent.")
        except Exception as e:
            logger.error(f"Failed to initialize GeminiClient within MetadataAgent: {e}", exc_info=True)
            self.gemini_client = None

        # Shared execution engine
        self.executor = GeminiTaskExecutor(self.gemini_client)
        
        # Single responsibility components
        self.tag_extractor = TagExtractor(self.executor)
        self.keyword_extractor = KeywordExtractor(self.executor)
        self.style_classifier = StyleClassifier(self.executor)
        self.language_detector = LanguageDetector(self.executor)
        self.description_generator = DescriptionGenerator(self.executor)
        self.title_generator = TitleGenerator(self.executor)

    def extract_tags(self, text: str) -> List[str]:
        return self.tag_extractor.extract(text).tags

    def extract_keywords(self, text: str) -> List[str]:
        return self.keyword_extractor.extract(text).keywords

    def classify_style(self, text: str) -> Dict[str, Any]:
        return dataclasses.asdict(self.style_classifier.extract(text))

    def generate_description(self, text: str) -> Dict[str, Any]:
        return dataclasses.asdict(self.description_generator.extract(text))

    def generate_metadata(self, text: str) -> Dict[str, Any]:
        try:
            result = MetadataResult(
                tags=self.tag_extractor.extract(text).tags,
                keywords=self.keyword_extractor.extract(text).keywords,
                style=self.style_classifier.extract(text),
                description=self.description_generator.extract(text)
            )
            return result.to_dict()
        except Exception as e:
            logger.error(f"Error in generate_metadata: {e}", exc_info=True)
            return {
                "tags": ["calligraphy"],
                "keywords": ["keyword"],
                "style": {"style": "Unknown", "confidence": 0, "reason": "error"},
                "description": {"description": "No description available."}
            }

    def process_metadata(self, text: str) -> Dict[str, Any]:
        try:
            metadata = self.generate_metadata(text)
            return {
                "status": "success",
                "metadata": metadata,
                "results": metadata,
                "count": len(metadata)
            }
        except Exception as e:
            logger.error(f"Error in process_metadata: {e}", exc_info=True)
            return {
                "status": "error",
                "metadata": {},
                "results": {},
                "count": 0
            }

    # =========================================================================
    # Backward Compatibility Methods
    # =========================================================================

    def extract_title(self, image_data: Any = None, text_description: str = "") -> str:
        return self.title_generator.extract(text_description).title

    def extract_style(self, image_data: Any = None, text_description: str = "") -> str:
        return self.style_classifier.extract(text_description).style

    def extract_language(self, image_data: Any = None, text_description: str = "") -> str:
        return self.language_detector.extract(text_description).language

    def generate_tags(self, image_data: Any = None, text_description: str = "") -> List[str]:
        return self.extract_tags(text_description)

    def analyze_post(self, image_data: Any = None, text_description: str = "") -> Dict[str, Any]:
        try:
            return {
                "title": self.extract_title(image_data, text_description),
                "style": self.extract_style(image_data, text_description),
                "language": self.extract_language(image_data, text_description),
                "tags": self.generate_tags(image_data, text_description),
                "description": self.generate_description(text_description).get("description", "No description available."),
                "difficulty": "Beginner"
            }
        except Exception as e:
            logger.error(f"Error in analyze_post legacy method: {e}", exc_info=True)
            return {
                "title": "Error Processing Post",
                "style": "Unknown",
                "language": "Unknown",
                "tags": [],
                "description": "An error occurred during metadata extraction.",
                "difficulty": "Unknown"
            }
