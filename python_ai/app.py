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
import json
from dotenv import load_dotenv
import os
from google import genai
from google.genai import types
from gemini_client import GeminiClient
from PIL import Image
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
load_dotenv()
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
def handle_ai_request():
    payload = request.get_json(force=True) # Grabs the clean JSON we fixed in PHP!
    
    task = payload.get("task_type")
    filters = payload.get("filters", {})
    
    prompt_text = filters.get("prompt")
    img_path = filters.get("image_path")
    media_type = filters.get("media_type", "image")
    
    gemini = GeminiClient()
    
    if task == "analyze":
        sys_rules = """You are a professional calligraphy instructor.

Analyze ONLY the uploaded calligraphy artwork.

Ignore completely:
- username
- title
- description
- likes
- comments
- filename
- upload history
- artist reputation

Evaluate the artwork based on a fixed weighted scoring rubric of these 7 categories:
1. Stroke consistency
2. Letter formation
3. Spacing
4. Rhythm
5. Composition
6. Contrast
7. Overall craftsmanship

The final score MUST be calculated only from the seven evaluation categories above.

Never estimate a score.

Never adjust the score because of artistic style, reputation, popularity, title, filename, or personal preference.

Two visually identical artworks must receive the same score.

Minor score variation between identical images should be avoided.

Round the final score to the nearest multiple of 5.

Return ONLY a valid JSON object.
Do not include markdown.
Do not include explanations.

The JSON MUST have exactly these fields:
{
    "style": "string",
    "score": integer from 0-100,
    "tags": ["string","string"],
    "stroke_analysis": "string",
    "composition_analysis": "string",
    "improvement_suggestions": "string"
}"""

        json_result = gemini.analyze_multimodal(
            prompt=prompt_text,
            image_path=img_path,
            system_instruction=sys_rules
        )

        logging.info("Gemini raw response:")
        logging.info(json_result)

        # try:
        #     parsed = json.loads(json_result)

        #     if isinstance(parsed, dict):
        #         parsed["success"] = True

        #         return jsonify(parsed), 200

        # except json.JSONDecodeError:
        #     logging.exception("Gemini returned invalid JSON")

        #     return jsonify({
        #         "success": False,
        #         "error": "Invalid JSON from Gemini",
        #         "raw": json_result
        #     }), 500
        try:
            print("\n========== RAW GEMINI RESPONSE ==========")
            print(repr(json_result))
            
            cleaned = json_result.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            parsed = json.loads(cleaned)

            if isinstance(parsed, dict):
                required_keys = ["style", "score", "tags", "stroke_analysis", "composition_analysis", "improvement_suggestions"]
                for k in required_keys:
                    if k not in parsed:
                        parsed[k] = [] if k == "tags" else ("" if isinstance(k, str) else 0)
                parsed["success"] = True

            return jsonify(parsed), 200

        except json.JSONDecodeError:
            logging.exception("Gemini returned invalid JSON")
            return jsonify({
                "success": False,
                "error": "Invalid JSON from Gemini",
                "raw": json_result
            }), 500
            
    elif task == "evaluate":
        if media_type == "video":
            sys_rules = """You are an AI content moderator and professional calligraphy instructor.

Determine whether the PRIMARY subject of the uploaded media is handwritten calligraphy or the creation of handwritten calligraphy.
Be reasonably tolerant.

Automatically APPROVE media containing:
- handwritten calligraphy
- finished calligraphy artwork
- calligraphy practice sheets
- calligraphy exercises
- people writing calligraphy
- calligraphy demonstrations
- calligraphy tutorial videos
- close-up videos of handwriting
- brushes, pens, ink, nibs, paper or tools being actively used for calligraphy
- work-in-progress calligraphy
- mixed scenes where calligraphy is clearly the main focus
- artwork where backgrounds contain unrelated objects but the primary focus is calligraphy

Reject ONLY when the uploaded media is clearly unrelated, including:
- selfies
- portraits unrelated to calligraphy
- landscapes
- vehicles
- pets
- food
- gaming
- memes
- random videos
- ordinary photography
- content with no meaningful calligraphy present

Moderation behaviour:
- If calligraphy is the primary subject, approve the upload (set approved to true).
- If confidence is moderate but calligraphy is still the obvious focus, approve the upload (set approved to true).
- Use needs_review to true only when genuinely uncertain.
- Reject (set approved to false, needs_review to false) only when there is strong evidence that the media is unrelated to calligraphy.

The AI should not require perfectly isolated calligraphy artwork.
The AI should understand that real users upload photographs and videos with natural backgrounds, hands, desks, lighting, and surrounding objects.

Evaluate the uploaded video based on:
- Content moderation
- Calligraphy relevance
- Safety review
- Video quality
- Artistic evaluation
- Overall recommendation

Return ONLY a valid JSON object.
Do not include markdown or explanations.

The JSON MUST have exactly these fields:
{
    "approved": boolean,
    "needs_review": boolean,
    "relevance_score": integer 0-100,
    "moderation_reason": "string (explain if not approved)",
    "style": "string",
    "score": integer 0-100,
    "tags": ["string","string"],
    "stroke_analysis": "string",
    "composition_analysis": "string",
    "improvement_suggestions": "string"
}"""
        else:
            sys_rules = """You are an AI content moderator and professional calligraphy instructor.

Determine whether the PRIMARY subject of the uploaded media is handwritten calligraphy or the creation of handwritten calligraphy.
Be reasonably tolerant.

Automatically APPROVE media containing:
- handwritten calligraphy
- finished calligraphy artwork
- calligraphy practice sheets
- calligraphy exercises
- people writing calligraphy
- calligraphy demonstrations
- calligraphy tutorial videos
- close-up videos of handwriting
- brushes, pens, ink, nibs, paper or tools being actively used for calligraphy
- work-in-progress calligraphy
- mixed scenes where calligraphy is clearly the main focus
- artwork where backgrounds contain unrelated objects but the primary focus is calligraphy

Reject ONLY when the uploaded media is clearly unrelated, including:
- selfies
- portraits unrelated to calligraphy
- landscapes
- vehicles
- pets
- food
- gaming
- memes
- random videos
- ordinary photography
- content with no meaningful calligraphy present

Moderation behaviour:
- If calligraphy is the primary subject, approve the upload (set approved to true).
- If confidence is moderate but calligraphy is still the obvious focus, approve the upload (set approved to true).
- Use needs_review to true only when genuinely uncertain.
- Reject (set approved to false, needs_review to false) only when there is strong evidence that the media is unrelated to calligraphy.

The AI should not require perfectly isolated calligraphy artwork.
The AI should understand that real users upload photographs and videos with natural backgrounds, hands, desks, lighting, and surrounding objects.

If the artwork is approved or needs review, evaluate it based on a fixed weighted scoring rubric of these 7 categories:
1. Stroke consistency
2. Letter formation
3. Spacing
4. Rhythm
5. Composition
6. Contrast
7. Overall craftsmanship

The final score MUST be calculated only from the seven evaluation categories above.
Never estimate a score.
Never adjust the score because of artistic style, reputation, popularity, title, filename, or personal preference.
Two visually identical artworks must receive the same score.
Minor score variation between identical images should be avoided.
Round the final score to the nearest multiple of 5.

Ignore completely:
- username
- title
- description
- likes
- comments
- filename
- upload history
- artist reputation

Return ONLY a valid JSON object.
Do not include markdown or explanations.

The JSON MUST have exactly these fields:
{
    "approved": boolean,
    "needs_review": boolean,
    "relevance_score": integer 0-100,
    "moderation_reason": "string (explain if not approved)",
    "style": "string",
    "score": integer 0-100,
    "tags": ["string","string"],
    "stroke_analysis": "string",
    "composition_analysis": "string",
    "improvement_suggestions": "string"
}"""
        try:
            logging.info(f"Starting evaluation for: {img_path}")
            
            if media_type == "video":
                import time
                media_obj = gemini.client.files.upload(file=img_path)
                
                # Poll until the video is active or failed
                start_time = time.time()
                timeout = 180
                
                while media_obj.state.name not in ("ACTIVE", "FAILED"):
                    if time.time() - start_time > timeout:
                        raise Exception("Video processing timed out after 180 seconds.")
                    time.sleep(2)
                    media_obj = gemini.client.files.get(name=media_obj.name)
                    
                if media_obj.state.name == "FAILED":
                    raise Exception("Video processing failed on Gemini servers.")
                elif media_obj.state.name != "ACTIVE":
                    raise Exception(f"Video is in an unexpected state: {media_obj.state.name}")
            else:
                media_obj = Image.open(img_path)
            
            response = gemini.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[sys_rules, prompt_text, media_obj],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.0
                )
            )
            
            cleaned = response.text.strip()
            if cleaned.startswith("```json"): cleaned = cleaned[7:]
            elif cleaned.startswith("```"): cleaned = cleaned[3:]
            if cleaned.endswith("```"): cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            parsed = json.loads(cleaned)

            if isinstance(parsed, dict):
                required_keys = ["approved", "needs_review", "relevance_score", "moderation_reason", "style", "score", "tags", "stroke_analysis", "composition_analysis", "improvement_suggestions"]
                for k in required_keys:
                    if k not in parsed:
                        if k in ["approved", "needs_review"]: parsed[k] = False
                        elif k == "tags": parsed[k] = []
                        elif "score" in k: parsed[k] = 0
                        else: parsed[k] = ""
                    else:
                        if k in ["approved", "needs_review"]:
                            if isinstance(parsed[k], str):
                                parsed[k] = parsed[k].lower() == 'true'
                            else:
                                parsed[k] = bool(parsed[k])
                parsed["success"] = True
                
            return jsonify(parsed), 200

        except Exception as e:
            logging.error(f"Evaluation AI failed: {str(e)}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
            
    elif task == "moderate":
        sys_rules = """You are an AI content moderator for a calligraphy website.

Determine whether the PRIMARY subject of the uploaded media is handwritten calligraphy or the creation of handwritten calligraphy.
Be reasonably tolerant.

Automatically APPROVE media containing:
- handwritten calligraphy
- finished calligraphy artwork
- calligraphy practice sheets
- calligraphy exercises
- people writing calligraphy
- calligraphy demonstrations
- calligraphy tutorial videos
- close-up videos of handwriting
- brushes, pens, ink, nibs, paper or tools being actively used for calligraphy
- work-in-progress calligraphy
- mixed scenes where calligraphy is clearly the main focus
- artwork where backgrounds contain unrelated objects but the primary focus is calligraphy

Reject ONLY when the uploaded media is clearly unrelated, including:
- selfies
- portraits unrelated to calligraphy
- landscapes
- vehicles
- pets
- food
- gaming
- memes
- random videos
- ordinary photography
- content with no meaningful calligraphy present

Return ONLY a valid JSON object.
Do not include markdown or explanations outside the JSON.

The JSON MUST have exactly these fields:
{
    "status": "Approved", 
    "relevance_score": 90,
    "reason": "string"
}

Status rules:
- Approved: Calligraphy is the primary subject, or confidence is moderate but calligraphy is still the obvious focus.
- Review: Genuinely uncertain.
- Flagged: Strong evidence that the media is unrelated to calligraphy.
"""
        try:
            logging.info(f"Starting moderation for: {img_path}")
            image_obj = Image.open(img_path)
            
            response = gemini.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[sys_rules, prompt_text, image_obj],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2
                )
            )
            
            parsed = json.loads(response.text)
            parsed["success"] = True
            
            # Ensure valid status
            if parsed.get("status") not in ["Approved", "Review", "Flagged"]:
                parsed["status"] = "Review"
                
            return jsonify(parsed), 200

        except Exception as e:
            logging.error(f"Moderation AI failed: {str(e)}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    return jsonify({
        "success": False, 
        "error": "Invalid or missing task_type"
    }), 400

if __name__ == "__main__":
    logging.info("Starting Calligraphy Central AI Service...")
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
