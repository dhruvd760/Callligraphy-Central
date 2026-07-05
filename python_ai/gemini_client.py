"""
Low-level client wrapper for interacting with the Google Gemini API (Modern SDK).
Handles Text, JSON enforcement, and Multimodal Image processing.
"""
import json
import logging
import os
from google import genai
from google.genai import types
from PIL import Image

logger = logging.getLogger(__name__)

class GeminiClient:
    """
    A resilient gateway for the Gemini API using the official `google-genai` SDK.
    """

    def __init__(self):
        logger.info("Initializing GeminiClient...")
        
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY environment variable is missing!")
        
        try:
            # 1. Modern SDK Client Initialization
            self.client = genai.Client(api_key=self.api_key)
            
            # Using the official standard model for complex multimodal & reasoning tasks
            self.model_name = "gemini-2.5-flash"
            logger.info(f"GeminiClient successfully initialized targeting '{self.model_name}'")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini SDK Client: {e}", exc_info=True)
            raise e

    def analyze_multimodal(self, prompt: str, image_path: str = None, system_instruction: str = None) -> str:
        """
        Sends Text AND an optional Image to Gemini, strictly demanding a JSON response.
        """
        if not prompt:
            return '{"error": "Empty prompt provided"}'

        contents_payload = [prompt]

        # 2. Automatically resolve and load the image if PHP sent a path
        if image_path:
            if os.path.exists(image_path):
                try:
                    logger.info(f"Loading visual asset from: {image_path}")
                    img = Image.open(image_path)
                    contents_payload.append(img)
                except Exception as e:
                    logger.error(f"Failed to parse image file at {image_path}: {e}")
                    return f'{{"error": "Corrupted or unreadable image file: {e}"}}'
            else:
                logger.error(f"Image path not found on server drive: {image_path}")
                return f'{{"error": "Image file does not exist at path: {image_path}"}}'

        try:
            logger.info(f"Dispatching payload to {self.model_name}...")
            
            # 3. Configure strict JSON output so your PHP json_decode() never fails
            config = types.GenerateContentConfig(
                max_output_tokens=2048,
                temperature=0.0, # Low temperature = more consistent, factual JSON
                response_mime_type="application/json",
                system_instruction=system_instruction
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents_payload,
                config=config
            )

            return response.text

        except Exception as e:
            logger.error(f"Gemini API Execution Error: {e}", exc_info=True)
            return f'{{"error": "AI generation failed: {str(e)}"}}'

    def generate_response(self, prompt: str) -> str:
        """
        Standard legacy text-only fallback method.
        """
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"Standard generation failed: {e}")
            return "Unable to generate response."