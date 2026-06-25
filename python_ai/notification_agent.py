"""
Agent responsible for formatting, dynamically generating, and dispatching user alerts.

This NotificationAgent translates platform events (likes, comments, followers, mentor critiques,
or system announcements) into natural, concise, and friendly notification text by querying
the Gemini API via GeminiClient.
"""

import logging
from typing import Dict, Any
from gemini_client import GeminiClient

# Set up module-specific logger
logger = logging.getLogger(__name__)

class NotificationAgent:
    """
    NotificationAgent handles the generation and dispatching of user alerts.
    
    It constructs tailored system notifications, updates, and community alerts
    using a low-level Gemini API client wrapper.
    
    Future Extensibility plans:
    - Multimodal Context: Incorporate information about visual artwork to tailor
      feedback alerts or comments notifications (e.g. referencing specific style colors).
    - Conversation Memory: Tailor notifications based on user response rates or
      preferred notification tones.
    - Tool Calling / Semantic Routing: Integrate check-ins with user notification
      preferences databases or external email/push delivery networks.
    """

    def __init__(self) -> None:
        """
        Initialize the NotificationAgent.
        Instantiates a GeminiClient for sending notification text refinement requests.
        """
        logger.info("Initializing NotificationAgent...")
        try:
            self.gemini_client = GeminiClient()
            logger.info("GeminiClient successfully initialized in NotificationAgent.")
        except Exception as e:
            logger.error(f"Failed to initialize GeminiClient within NotificationAgent: {e}", exc_info=True)
            self.gemini_client = None

    def generate_notification(self, prompt: str) -> str:
        """
        Generates a dynamic, user-friendly notification message based on the input request.

        Args:
            prompt (str): The context or event trigger details.

        Returns:
            str: The generated notification text.
        """
        if not self.gemini_client:
            logger.error("GeminiClient is not available. Using basic fallback.")
            return "An event has occurred on your profile."

        # Detailed system instruction describing an expert notification assistant
        system_instruction = (
            "You are an expert notification assistant for Calligraphy Central, a community for calligraphers. "
            "Your task is to generate concise, friendly, and natural notification copy "
            "that is polite, engaging, and directly summarizes the event. "
            "Return only the final, ready-to-display text response without any markdown, metadata, or quotes."
        )

        full_prompt = f"{system_instruction}\n\nEvent Context:\n{prompt}"
        
        try:
            logger.info("Generating notification copy via Gemini...")
            response = self.gemini_client.generate_response(full_prompt)
            return response.strip().strip('"').strip("'")
        except Exception as e:
            logger.error(f"Error in generate_notification: {e}", exc_info=True)
            return "An event has occurred on your profile."

    def send_like_notification(self, user_id: Any) -> Dict[str, Any]:
        """
        Formats a notification indicating a user's post received a like.

        Args:
            user_id: The ID of the user receiving the notification.

        Returns:
            Dict[str, Any]: A dictionary containing user_id and the generated message.
        """
        try:
            prompt = f"Format a notification for user {user_id} whose calligraphy post was liked by another community member."
            message = self.generate_notification(prompt)
            return {
                "user_id": user_id,
                "message": message
            }
        except Exception as e:
            logger.error(f"Error in send_like_notification: {e}", exc_info=True)
            return {
                "user_id": user_id,
                "message": "Someone liked your calligraphy post!"
            }

    def send_comment_notification(self, user_id: Any) -> Dict[str, Any]:
        """
        Formats a notification indicating a user's post received a comment.

        Args:
            user_id: The ID of the user receiving the notification.

        Returns:
            Dict[str, Any]: A dictionary containing user_id and the generated message.
        """
        try:
            prompt = f"Format a notification for user {user_id} who received a comment on their calligraphy post."
            message = self.generate_notification(prompt)
            return {
                "user_id": user_id,
                "message": message
            }
        except Exception as e:
            logger.error(f"Error in send_comment_notification: {e}", exc_info=True)
            return {
                "user_id": user_id,
                "message": "Someone commented on your calligraphy post!"
            }

    def send_follow_notification(self, user_id: Any) -> Dict[str, Any]:
        """
        Formats a notification indicating a user gained a new follower.

        Args:
            user_id: The ID of the user receiving the notification.

        Returns:
            Dict[str, Any]: A dictionary containing user_id and the generated message.
        """
        try:
            prompt = f"Format a notification for user {user_id} who gained a new follower in the calligraphy community."
            message = self.generate_notification(prompt)
            return {
                "user_id": user_id,
                "message": message
            }
        except Exception as e:
            logger.error(f"Error in send_follow_notification: {e}", exc_info=True)
            return {
                "user_id": user_id,
                "message": "You have a new follower!"
            }

    def send_mentor_notification(self, user_id: Any) -> Dict[str, Any]:
        """
        Formats a notification indicating that the MentorAgent has generated new feedback.

        Args:
            user_id: The ID of the user receiving the notification.

        Returns:
            Dict[str, Any]: A dictionary containing user_id and the generated message.
        """
        try:
            prompt = (
                f"Format a notification for user {user_id} indicating that their virtual calligraphy mentor "
                "has analyzed their latest practice piece and posted new feedback."
            )
            message = self.generate_notification(prompt)
            return {
                "user_id": user_id,
                "message": message
            }
        except Exception as e:
            logger.error(f"Error in send_mentor_notification: {e}", exc_info=True)
            return {
                "user_id": user_id,
                "message": "Your virtual mentor has new feedback for your latest practice."
            }

    def send_system_notification(self, message: str) -> Dict[str, Any]:
        """
        Formats a general platform-wide system notification.

        Args:
            message (str): The raw system announcement message to refine.

        Returns:
            Dict[str, Any]: A dictionary with user_id 'all' and the refined message.
        """
        try:
            prompt = f"Refine the following system-wide announcement to be concise, professional, and clear: '{message}'"
            refined_message = self.generate_notification(prompt)
            return {
                "user_id": "all",
                "message": refined_message
            }
        except Exception as e:
            logger.error(f"Error in send_system_notification: {e}", exc_info=True)
            return {
                "user_id": "all",
                "message": message
            }

    def notify_user(self, notification_type: str = "system", filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main orchestration method for the NotificationAgent.
        
        Delegates notification copy production to the corresponding type and returns 
        the final dispatch payload.

        Args:
            notification_type (str): The type of event (like, comment, follow, mentor, system).
            filters (Dict[str, Any]): Details of the notification context (e.g. user_id, message).

        Returns:
            Dict[str, Any]: A structured dictionary containing dispatch payload and event details.
        """
        try:
            logger.info(f"Orchestrating notification generation for type: {notification_type}")
            notification_data = None
            
            if filters is None:
                filters = {}

            # Route to the appropriate notification strategy
            if notification_type == "like" and "user_id" in filters:
                notification_data = self.send_like_notification(filters["user_id"])
            elif notification_type == "comment" and "user_id" in filters:
                notification_data = self.send_comment_notification(filters["user_id"])
            elif notification_type == "follow" and "user_id" in filters:
                notification_data = self.send_follow_notification(filters["user_id"])
            elif notification_type == "mentor" and "user_id" in filters:
                notification_data = self.send_mentor_notification(filters["user_id"])
            elif notification_type == "system" and "message" in filters:
                notification_data = self.send_system_notification(filters["message"])
            else:
                logger.warning(f"Invalid notification_type or missing required filter keys: {notification_type}")
                notification_data = {"error": "Invalid notification_type or missing filters."}

            return {
                "notification_type": notification_type,
                "data": notification_data,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error in notify_user orchestration: {e}", exc_info=True)
            return {
                "notification_type": "error",
                "data": {},
                "status": "failed"
            }
