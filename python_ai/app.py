"""
Main application entry point for the AI layer.
Provides the HTTP/REST API endpoints for the PHP application to interact with.

Future Gemini Integration:
The endpoints below currently route to placeholder agents. In the future, integrating Gemini will allow:
- Semantic routing: The Orchestrator can use an LLM to dynamically determine which agent handles an ambiguous query.
- Conversational memory: Maintaining a history of interactions to provide context-aware responses.
- Tool calling: Agents could call out to external APIs or databases directly via Gemini function calls.
- Image understanding: Passing image data directly to Gemini Vision to critique calligraphy style.
- Personalized responses: Tailoring output language and tone based on user preferences.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from orchestrator import Orchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize Flask application
app = Flask(__name__)

# Enable CORS for PHP application communication
CORS(app)

# Initialize the AI System Master Orchestrator
# This ensures agents are loaded once into memory when the server starts
orchestrator = Orchestrator()

@app.route('/', methods=['GET'])
def root():
    """Root endpoint to verify the service is running."""
    return jsonify({
        "message": "Calligraphy Central AI API running",
        "status": "success"
    }), 200

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for deployment monitoring."""
    return jsonify({
        "status": "ok"
    }), 200

@app.route('/ai', methods=['POST'])
def ai_endpoint():
    """
    Main entry point for all AI processing requests from the PHP layer.
    Accepts JSON payloads, validates inputs, and delegates to the Orchestrator.
    """
    try:
        data = request.get_json()
        
        # 7. Input Validation: Check for valid JSON
        if not data:
            logging.error("No JSON payload received.")
            return jsonify({
                "status": "failed",
                "error": "No JSON payload received."
            }), 400

        task_type = data.get("task_type", "")
        
        # 7. Input Validation: Check for task_type
        if not task_type:
            logging.error("task_type is missing from payload.")
            return jsonify({
                "status": "failed",
                "error": "task_type is required."
            }), 400

        filters = data.get("filters", {})

        # Delegate entirely to the Orchestrator (No business logic in app.py)
        response = orchestrator.process_request(task_type, filters)

        return jsonify(response), 200

    except Exception as e:
        # 8. Exception Handling: Ensure the server never crashes on bad requests
        logging.error(f"Unexpected error in /ai endpoint: {e}")
        return jsonify({
            "status": "failed",
            "error": str(e)
        }), 500

if __name__ == "__main__":
    logging.info("Starting Calligraphy Central AI Service...")
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
