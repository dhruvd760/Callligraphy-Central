"""
Agent responsible for scanning text and community submissions for policy violations, spam, and abuse.

This ModerationAgent implements real-time text analysis using Gemini via GeminiClient, 
ensuring the Calligraphy Central platform remains safe, welcoming, and spam-free.
"""

import json
import logging
from typing import Dict, Any, List
from gemini_client import GeminiClient

# Set up module-specific logger
logger = logging.getLogger(__name__)

class ModerationAgent:
    """
    ModerationAgent handles safety, compliance, and community standards checks.
    
    It validates posts, comments, engagements, and profiles, and classifies
    violations using the Google Gemini model.
    
    Future Extensibility plans:
    - Multimodal Safety (Vision): Send upload images to Gemini Vision to detect graphic content,
      violating watermarks, or irrelevant imagery.
    - Conversation Memory: Track warnings given to specific users to automatically escalate
      repeated infractions.
    - Tool Calling / Semantic Routing: Automatically trigger admin escalation tickets or block
      database records when critical violations (e.g. malicious code Injection) are detected.
    """

    def __init__(self) -> None:
        """
        Initialize the ModerationAgent.
        Instantiates a GeminiClient for sending moderation requests.
        """
        logger.info("Initializing ModerationAgent...")
        try:
            self.gemini_client = GeminiClient()
            logger.info("GeminiClient successfully initialized in ModerationAgent.")
        except Exception as e:
            logger.error(f"Failed to initialize GeminiClient within ModerationAgent: {e}", exc_info=True)
            self.gemini_client = None

    def _parse_gemini_json(self, response_text: str, default_val: Dict[str, Any]) -> Dict[str, Any]:
        """
        Helper method to clean and parse JSON responses from Gemini.
        """
        try:
            cleaned = response_text.strip()
            # Handle markdown code fences if returned by the model
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            return json.loads(cleaned)
        except Exception as e:
            logger.warning(f"Failed to parse JSON from Gemini response: {e}. Raw response: {response_text}")
            return default_val

    def detect_spam(self, text: str) -> Dict[str, Any]:
        """
        Analyzes text to detect spam patterns, malicious links, or repetitive garbage.

        Args:
            text (str): The text content to analyze.

        Returns:
            Dict[str, Any]: A dictionary containing is_spam, confidence, and explanation.
        """
        if not self.gemini_client:
            logger.error("GeminiClient is not available. detect_spam returning fallback.")
            return {"is_spam": False, "confidence": 0.0, "reason": "GeminiClient unavailable."}

        try:
            prompt = (
                "You are an expert community moderator for Calligraphy Central. "
                "Analyze the following text and determine if it is spam, unsolicited advertising, "
                "excessive self-promotion, phishing links, or gibberish. "
                "Respond ONLY with a JSON object in this format:\n"
                "{\n"
                "  \"is_spam\": true/false,\n"
                "  \"confidence\": 0.0 to 1.0,\n"
                "  \"reason\": \"A professional explanation of the decision.\"\n"
                "}"
            )
            response = self.gemini_client.generate_response(f"{prompt}\n\nText: {text}")
            default_val = {"is_spam": False, "confidence": 0.5, "reason": "Parsing error fallback."}
            return self._parse_gemini_json(response, default_val)
        except Exception as e:
            logger.error(f"Error in detect_spam: {e}", exc_info=True)
            return {"is_spam": False, "confidence": 0.0, "reason": "Error during analysis."}

    def detect_offensive_content(self, text: str) -> Dict[str, Any]:
        """
        Scans text for hate speech, harassment, or other offensive content.

        Args:
            text (str): The text content to scan.

        Returns:
            Dict[str, Any]: A dictionary containing is_offensive, severity, and reason.
        """
        if not self.gemini_client:
            logger.error("GeminiClient is not available. detect_offensive_content returning fallback.")
            return {"is_offensive": False, "severity": "unknown", "reason": "GeminiClient unavailable."}

        try:
            prompt = (
                "You are an expert community moderator for Calligraphy Central. "
                "Analyze the text for offensive language, hate speech, abuse, or harassment. "
                "Respond ONLY with a JSON object in this format:\n"
                "{\n"
                "  \"is_offensive\": true/false,\n"
                "  \"severity\": \"low/medium/high\",\n"
                "  \"reason\": \"A professional explanation of the classification.\"\n"
                "}"
            )
            response = self.gemini_client.generate_response(f"{prompt}\n\nText: {text}")
            default_val = {"is_offensive": False, "severity": "low", "reason": "Parsing error fallback."}
            return self._parse_gemini_json(response, default_val)
        except Exception as e:
            logger.error(f"Error in detect_offensive_content: {e}", exc_info=True)
            return {"is_offensive": False, "severity": "unknown", "reason": "Error during analysis."}

    def detect_duplicate_posts(self, post_data: Any) -> Dict[str, Any]:
        """
        Checks if a user is repeatedly submitting the exact same or highly similar posts.

        Args:
            post_data: Content or metadata of the post to analyze.

        Returns:
            Dict[str, Any]: A dictionary containing is_duplicate, duplicate_id, and similarity_score.
        """
        if not self.gemini_client:
            logger.error("GeminiClient is not available. detect_duplicate_posts returning fallback.")
            return {"is_duplicate": False, "duplicate_id": None, "similarity_score": 0.0}

        try:
            text_to_check = str(post_data)
            prompt = (
                "Analyze the following submission details. Determine if it represents duplicate text/spamming features. "
                "Respond ONLY with a JSON object in this format:\n"
                "{\n"
                "  \"is_duplicate\": true/false,\n"
                "  \"duplicate_id\": null,\n"
                "  \"similarity_score\": 0.0 to 1.0\n"
                "}"
            )
            response = self.gemini_client.generate_response(f"{prompt}\n\nSubmission: {text_to_check}")
            default_val = {"is_duplicate": False, "duplicate_id": None, "similarity_score": 0.0}
            return self._parse_gemini_json(response, default_val)
        except Exception as e:
            logger.error(f"Error in detect_duplicate_posts: {e}", exc_info=True)
            return {"is_duplicate": False, "duplicate_id": None, "similarity_score": 0.0}

    def detect_fake_engagement(self, user_id: Any) -> Dict[str, Any]:
        """
        Analyzes user behavior metrics to detect bots or engagement farming.

        Args:
            user_id: The identifier of the user to monitor.

        Returns:
            Dict[str, Any]: A dictionary containing is_fake_engagement, risk_level, and action_recommended.
        """
        if not self.gemini_client:
            logger.error("GeminiClient is not available. detect_fake_engagement returning fallback.")
            return {"is_fake_engagement": False, "risk_level": "low", "action_recommended": "none"}

        try:
            prompt = (
                "Analyze the following user profile activity summary. Flag potential artificial engagement or bot behavior. "
                "Respond ONLY with a JSON object in this format:\n"
                "{\n"
                "  \"is_fake_engagement\": true/false,\n"
                "  \"risk_level\": \"low/medium/high\",\n"
                "  \"action_recommended\": \"none/monitor/flag/block\"\n"
                "}"
            )
            response = self.gemini_client.generate_response(f"{prompt}\n\nUser Profile data: {user_id}")
            default_val = {"is_fake_engagement": False, "risk_level": "low", "action_recommended": "none"}
            return self._parse_gemini_json(response, default_val)
        except Exception as e:
            logger.error(f"Error in detect_fake_engagement: {e}", exc_info=True)
            return {"is_fake_engagement": False, "risk_level": "unknown", "action_recommended": "none"}

    def moderate_post(self, post_text: str) -> Dict[str, Any]:
        """
        Analyzes calligraphy post text to ensure it conforms to community guidelines.

        Args:
            post_text (str): The raw text of the post.

        Returns:
            Dict[str, Any]: A safety assessment result dictionary.
        """
        if not self.gemini_client:
            return {"is_safe": True, "reason": "GeminiClient unavailable.", "flagged_categories": []}

        try:
            prompt = (
                "You are an expert community moderator for Calligraphy Central. "
                "Evaluate the text of this new post. Flag spam, harassment, hate speech, or explicit text. "
                "Respond ONLY with a JSON object in this format:\n"
                "{\n"
                "  \"is_safe\": true/false,\n"
                "  \"reason\": \"Professional summary.\",\n"
                "  \"flagged_categories\": []\n"
                "}"
            )
            response = self.gemini_client.generate_response(f"{prompt}\n\nPost: {post_text}")
            default_val = {"is_safe": True, "reason": "Parsing error fallback.", "flagged_categories": []}
            return self._parse_gemini_json(response, default_val)
        except Exception as e:
            logger.error(f"Error in moderate_post: {e}", exc_info=True)
            return {"is_safe": True, "reason": "Error during analysis fallback.", "flagged_categories": []}

    def check_comment(self, comment_text: str) -> Dict[str, Any]:
        """
        Scans a comment for toxicity, spam, abuse, or rule violations.

        Args:
            comment_text (str): The comment text to evaluate.

        Returns:
            Dict[str, Any]: An assessment dictionary.
        """
        if not self.gemini_client:
            return {"is_safe": True, "is_toxic": False, "reason": "GeminiClient unavailable."}

        try:
            prompt = (
                "You are an expert community moderator for Calligraphy Central. "
                "Analyze this comment for harassment, toxic language, extreme profanity, or spam. "
                "Respond ONLY with a JSON object in this format:\n"
                "{\n"
                "  \"is_safe\": true/false,\n"
                "  \"is_toxic\": true/false,\n"
                "  \"reason\": \"Professional explanation.\"\n"
                "}"
            )
            response = self.gemini_client.generate_response(f"{prompt}\n\nComment: {comment_text}")
            default_val = {"is_safe": True, "is_toxic": False, "reason": "Parsing error fallback."}
            return self._parse_gemini_json(response, default_val)
        except Exception as e:
            logger.error(f"Error in check_comment: {e}", exc_info=True)
            return {"is_safe": True, "is_toxic": False, "reason": "Error during analysis fallback."}

    def detect_profanity(self, text: str) -> Dict[str, Any]:
        """
        Detects vulgar, offensive, or profane content within the text.

        Args:
            text (str): The text to review.

        Returns:
            Dict[str, Any]: An assessment dictionary.
        """
        if not self.gemini_client:
            return {"has_profanity": False, "profanity_count": 0, "reason": "GeminiClient unavailable."}

        try:
            prompt = (
                "Analyze the text for profanity, slurs, or highly vulgar language. "
                "Respond ONLY with a JSON object in this format:\n"
                "{\n"
                "  \"has_profanity\": true/false,\n"
                "  \"profanity_count\": 0,\n"
                "  \"reason\": \"Brief explanation.\"\n"
                "}"
            )
            response = self.gemini_client.generate_response(f"{prompt}\n\nText: {text}")
            default_val = {"has_profanity": False, "profanity_count": 0, "reason": "Parsing error fallback."}
            return self._parse_gemini_json(response, default_val)
        except Exception as e:
            logger.error(f"Error in detect_profanity: {e}", exc_info=True)
            return {"has_profanity": False, "profanity_count": 0, "reason": "Error during analysis fallback."}

    def detect_hate_speech(self, text: str) -> Dict[str, Any]:
        """
        Scans text for hate speech targeting groups based on race, religion, gender, identity, etc.

        Args:
            text (str): The text content to analyze.

        Returns:
            Dict[str, Any]: An assessment dictionary.
        """
        if not self.gemini_client:
            return {"is_hate_speech": False, "severity": "low", "reason": "GeminiClient unavailable."}

        try:
            prompt = (
                "Scan this text for hate speech, discrimination, slurs, or harassment targeting protected groups. "
                "Respond ONLY with a JSON object in this format:\n"
                "{\n"
                "  \"is_hate_speech\": true/false,\n"
                "  \"severity\": \"low/medium/high\",\n"
                "  \"reason\": \"Professional explanation.\"\n"
                "}"
            )
            response = self.gemini_client.generate_response(f"{prompt}\n\nText: {text}")
            default_val = {"is_hate_speech": False, "severity": "low", "reason": "Parsing error fallback."}
            return self._parse_gemini_json(response, default_val)
        except Exception as e:
            logger.error(f"Error in detect_hate_speech: {e}", exc_info=True)
            return {"is_hate_speech": False, "severity": "low", "reason": "Error during analysis fallback."}

    def review_content(self, text: str) -> Dict[str, Any]:
        """
        A general purpose content review that aggregates multiple moderation checks.

        Args:
            text (str): The raw content body.

        Returns:
            Dict[str, Any]: Safety evaluation outcome.
        """
        if not self.gemini_client:
            return {"is_safe": True, "flags": [], "explanation": "GeminiClient unavailable."}

        try:
            prompt = (
                "You are an expert community moderator for Calligraphy Central. "
                "Perform a thorough policy check. Review for spam, harassment, hate speech, and explicit material. "
                "Respond ONLY with a JSON object in this format:\n"
                "{\n"
                "  \"is_safe\": true/false,\n"
                "  \"flags\": [],\n"
                "  \"explanation\": \"Detailed review response.\"\n"
                "}"
            )
            response = self.gemini_client.generate_response(f"{prompt}\n\nContent: {text}")
            default_val = {"is_safe": True, "flags": [], "explanation": "Parsing error fallback."}
            return self._parse_gemini_json(response, default_val)
        except Exception as e:
            logger.error(f"Error in review_content: {e}", exc_info=True)
            return {"is_safe": True, "flags": [], "explanation": "Error during analysis fallback."}

    def review_post(self, review_type: str = "spam", filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main orchestration method for the ModerationAgent.
        
        Delegates to specific detection strategies based on review_type, and aggregates results.

        Args:
            review_type (str): The focus area (spam, offensive, duplicate, engagement).
            filters (Dict[str, Any]): Inputs details (e.g. text, post_data, user_id).

        Returns:
            Dict[str, Any]: The structured response.
        """
        try:
            logger.info(f"Orchestrating moderation review for type: {review_type}")
            assessment = None
            
            if filters is None:
                filters = {}

            # Route to the appropriate moderation strategy
            if review_type == "spam" and "text" in filters:
                assessment = self.detect_spam(filters["text"])
            elif review_type == "offensive" and "text" in filters:
                assessment = self.detect_offensive_content(filters["text"])
            elif review_type == "duplicate" and "post_data" in filters:
                assessment = self.detect_duplicate_posts(filters["post_data"])
            elif review_type == "engagement" and "user_id" in filters:
                assessment = self.detect_fake_engagement(filters["user_id"])
            else:
                logger.warning(f"Invalid review_type or missing required filter keys: {review_type}")
                assessment = {"error": "Invalid review_type or missing filters."}

            return {
                "review_type": review_type,
                "assessment": assessment,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error in review_post orchestration: {e}", exc_info=True)
            # Return a graceful fallback dictionary ensuring fail-open (allow by default if error)
            return {
                "review_type": "error",
                "assessment": {"is_safe": True, "reason": "Failed to analyze content due to error."},
                "status": "failed"
            }
