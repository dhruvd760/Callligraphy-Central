"""
Main workflow manager that receives requests from app.py and delegates to specific agents.
"""
import logging

from search_agent import SearchAgent
from recommendation_agent import RecommendationAgent
from mentor_agent import MentorAgent
from moderation_agent import ModerationAgent
from curator_agent import CuratorAgent
from notification_agent import NotificationAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class Orchestrator:
    """
    The Orchestrator acts as the central coordinator and master router for all AI operations.
    It receives standardized JSON payloads from the PHP application via app.py, interprets the 
    request type, and delegates the task to the appropriate specialized AI agent.
    
    Future: Will integrate Gemini models for 'semantic routing' and 'tool calling', 
    allowing the Orchestrator to dynamically decide which combination of agents is required 
    to fulfill complex, multi-step queries based on conversational context and memory.
    """

    def __init__(self):
        """
        Initializes the Orchestrator and pre-loads all specific AI agents.
        """
        try:
            logging.info("Initializing Orchestrator and loading agents...")
            self.search_agent = SearchAgent()
            self.recommendation_agent = RecommendationAgent()
            self.mentor_agent = MentorAgent()
            self.moderation_agent = ModerationAgent()
            self.curator_agent = CuratorAgent()
            self.notification_agent = NotificationAgent()
            logging.info("All agents loaded successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize Orchestrator agents: {e}")

    def search_posts(self, query):
        """
        Delegates search requests to the SearchAgent.
        Future: Gemini could rewrite the query for better semantic match retrieval.
        """
        try:
            return self.search_agent.search_posts(query)
        except Exception as e:
            logging.error(f"Error orchestrating search_posts: {e}")
            return {"status": "failed", "query": query, "results": [], "error": str(e)}

    def get_recommendations(self, recommendation_type="trending", filters=None):
        """
        Delegates recommendation requests to the RecommendationAgent.
        Future: Gemini could analyze user history to formulate a highly personalized context prompt.
        """
        try:
            return self.recommendation_agent.recommend_posts(recommendation_type, filters)
        except Exception as e:
            logging.error(f"Error orchestrating get_recommendations: {e}")
            return {"status": "failed", "recommendations": [], "error": str(e)}

    def get_mentoring(self, request_type="tips", filters=None):
        """
        Delegates mentorship and feedback requests to the MentorAgent.
        Future: Gemini could analyze the image and generate nuanced, generative feedback.
        """
        try:
            return self.mentor_agent.mentor_response(request_type, filters)
        except Exception as e:
            logging.error(f"Error orchestrating get_mentoring: {e}")
            return {"status": "failed", "advice": {}, "error": str(e)}

    def review_content(self, review_type="spam", filters=None):
        """
        Delegates policy and safety checks to the ModerationAgent.
        Future: Gemini safety filters could evaluate subtle context or nuanced abuse.
        """
        try:
            return self.moderation_agent.review_post(review_type, filters)
        except Exception as e:
            logging.error(f"Error orchestrating review_content: {e}")
            return {"status": "failed", "assessment": {"is_safe": True}, "error": str(e)}

    def get_curated_content(self, collection_type="featured", filters=None):
        """
        Delegates content curation requests to the CuratorAgent.
        Future: Gemini Vision models could assess aesthetics and compose thematic galleries.
        """
        try:
            return self.curator_agent.curate_content(collection_type, filters)
        except Exception as e:
            logging.error(f"Error orchestrating get_curated_content: {e}")
            return {"status": "failed", "data": [], "error": str(e)}

    def notify_user(self, notification_type="system", filters=None):
        """
        Delegates notification formatting and dispatching to the NotificationAgent.
        Future: Gemini could personalize notification language based on user tone preferences.
        """
        try:
            return self.notification_agent.notify_user(notification_type, filters)
        except Exception as e:
            logging.error(f"Error orchestrating notify_user: {e}")
            return {"status": "failed", "data": {}, "error": str(e)}

    def process_request(self, task_type, filters=None):
        """
        Master router for the Orchestrator. 
        Takes a task_type and a filters dictionary, then delegates to the appropriate agent wrapper.
        """
        try:
            logging.info(f"Processing request for task_type: {task_type}")
            
            if filters is None:
                filters = {}

            if task_type == "analyze":
                from analyze_agent import AnalyzeAgent
                agent = AnalyzeAgent()
                return agent.analyze(prompt=filters.get("prompt", "") or filters.get("description", ""))
                
            elif task_type == "search":
                return self.search_posts(filters.get("query", ""))
                
            elif task_type == "recommendations":
                return self.get_recommendations(
                    filters.get("recommendation_type", "trending"),
                    filters
                )
                
            elif task_type == "mentor":
                return self.get_mentoring(
                    filters.get("request_type", "tips"),
                    filters
                )
                
            elif task_type == "moderation":
                return self.review_content(
                    filters.get("review_type", "spam"),
                    filters
                )
                
            elif task_type == "curation":
                return self.get_curated_content(
                    filters.get("collection_type", "featured"),
                    filters
                )
                
            elif task_type == "notification":
                return self.notify_user(
                    filters.get("notification_type", "system"),
                    filters
                )
                
            else:
                logging.warning(f"Unknown task type received: {task_type}")
                return {
                    "status": "failed",
                    "error": "Unknown task type"
                }

        except Exception as e:
            logging.error(f"Error in process_request: {e}")
            return {
                "status": "failed",
                "error": "An unexpected error occurred during request processing."
            }
