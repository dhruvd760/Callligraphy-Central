import json
import logging
import os
from typing import Dict, Any
from gemini_client import GeminiClient

logger = logging.getLogger(__name__)

class AnalyzeAgent:
    def __init__(self):
        self.gemini_client = GeminiClient()
        self.schema_keys = [
            "style", 
            "score", 
            "tags", 
            "stroke_analysis", 
            "composition_analysis", 
            "improvement_suggestions"
        ]

    def _get_fallback(self) -> Dict[str, Any]:
        """Returns the standard fallback JSON schema when AI fails."""
        return {
            "style": "Unknown",
            "score": 0,
            "tags": [],
            "stroke_analysis": "Analysis unavailable.",
            "composition_analysis": "Analysis unavailable.",
            "improvement_suggestions": "Suggestions unavailable.",
            "success": False
        }

    def _validate_and_parse(self, response_text: str) -> Dict[str, Any]:
        """
        Strips markdown and validates the parsed JSON against required keys.
        Returns the parsed dictionary or raises ValueError.
        """
        cleaned = response_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            result = json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to decode JSON: {e}")

        # Ensure it is a dict
        if not isinstance(result, dict):
            raise ValueError("Parsed JSON is not a dictionary.")

        # Ensure required keys exist
        for key in self.schema_keys:
            if key not in result:
                # Add default padding for missing keys
                result[key] = [] if key == "tags" else ("" if isinstance(key, str) else 0)

        result["success"] = True
        return result

    def _build_prompt(self, user_prompt: str, media_type: str = "image") -> str:
        """Constructs the system prompt and strict JSON schema requirements."""
        schema_json = json.dumps({k: f"<{k}>" for k in self.schema_keys}, indent=2)
        
        if media_type == "video":
            return (
                "You are an expert calligraphy evaluator and professional instructor.\n\n"
                "Evaluate the uploaded video based on:\n"
                "- Content moderation\n"
                "- Calligraphy relevance\n"
                "- Safety review\n"
                "- Video quality\n"
                "- Artistic evaluation\n"
                "- Overall recommendation\n\n"
                "Return ONLY valid JSON.\n"
                "Do NOT return Markdown.\n"
                "Do NOT explain your reasoning.\n"
                "Start immediately with '{'.\n\n"
                f"{schema_json}"
            )
        else:
            return (
                "You are an expert calligraphy evaluator and professional instructor.\n\n"
                "Evaluate ONLY the visible handwriting in the uploaded artwork.\n"
                "Ignore completely:\n"
                "- title\n"
                "- description\n"
                "- username\n"
                "- filename\n"
                "- upload history\n\n"
                "Use exactly the same evaluation standards for every artwork.\n"
                "If two uploaded images are visually identical, they must receive nearly identical "
                "style classifications, tags, feedback and scores.\n\n"
                "Score according to this rubric:\n"
                "95-100 = Museum or professional exhibition quality\n"
                "90-94 = Excellent\n"
                "85-89 = Very Good\n"
                "80-84 = Good\n"
                "75-79 = Above Average\n"
                "70-74 = Average\n"
                "65-69 = Beginner\n"
                "60-64 = Needs Improvement\n"
                "Below 60 = Poor\n\n"
                "Provide constructive and specific feedback based only on the handwriting visible.\n"
                f"{user_prompt}\n\n"
                "Return ONLY valid JSON.\n"
                "Do NOT return Markdown.\n"
                "Do NOT explain your reasoning.\n"
                "Start immediately with '{'.\n\n"
                f"{schema_json}"
            )

    def analyze(self, image_path: str = "", prompt: str = "", media_type: str = "image") -> Dict[str, Any]:
        """
        Analyzes a calligraphy post and returns a structured critique.
        """
        if not self.gemini_client or not self.gemini_client.api_key:
            logger.error("Gemini API key missing. Returning fallback.")
            return self._get_fallback()

        full_prompt = self._build_prompt(prompt, media_type)
        
        try:
            response_text = self.gemini_client.generate_response(full_prompt)
            return self._validate_and_parse(response_text)
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return self._get_fallback()
