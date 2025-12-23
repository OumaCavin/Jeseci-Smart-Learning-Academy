"""
Flask Microservice for AI Content Generation
This service provides an HTTP API for the Jaclang backend to generate AI content
"""

import os
import sys
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_generator import sync_generate_lesson, ai_generator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)

# Configuration
AI_SERVICE_HOST = os.getenv("AI_SERVICE_HOST", "localhost")
AI_SERVICE_PORT = int(os.getenv("AI_SERVICE_PORT", "8001"))


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "ai-content-generator",
        "openai_available": ai_generator.available,
        "timestamp": str(__import__('datetime').datetime.now())
    })


@app.route('/generate', methods=['POST'])
def generate_content():
    """
    Generate AI content for educational lessons
    
    Expected JSON payload:
    {
        "concept_name": "Object-Oriented Programming",
        "domain": "Computer Science",
        "difficulty": "beginner",
        "related_concepts": ["Classes", "Inheritance", "Polymorphism"]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON payload provided"
            }), 400
        
        # Extract parameters
        concept_name = data.get('concept_name', '')
        domain = data.get('domain', 'General')
        difficulty = data.get('difficulty', 'beginner')
        related_concepts = data.get('related_concepts', [])
        
        if not concept_name:
            return jsonify({
                "success": False,
                "error": "concept_name is required"
            }), 400
        
        logger.info(f"Generating content for: {concept_name} ({difficulty})")
        
        # Generate content using OpenAI
        related_concepts_str = ",".join(related_concepts) if related_concepts else ""
        content = sync_generate_lesson(
            concept_name=concept_name,
            domain=domain,
            difficulty=difficulty,
            related_concepts_str=related_concepts_str
        )
        
        response = {
            "success": True,
            "concept_name": concept_name,
            "domain": domain,
            "difficulty": difficulty,
            "content": content,
            "related_concepts": related_concepts,
            "generated_at": str(__import__('datetime').datetime.now()),
            "source": "openai" if ai_generator.available else "fallback"
        }
        
        logger.info(f"Successfully generated content for {concept_name}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/status', methods=['GET'])
def service_status():
    """Get service status including OpenAI configuration"""
    return jsonify({
        "service": "ai-content-generator",
        "version": "1.0.0",
        "openai_configured": ai_generator.available,
        "openai_model": "gpt-4o-mini",
        "endpoints": {
            "/health": "GET - Health check",
            "/generate": "POST - Generate AI content",
            "/status": "GET - Service status"
        }
    })


if __name__ == '__main__':
    logger.info(f"Starting AI Content Generator Service on {AI_SERVICE_HOST}:{AI_SERVICE_PORT}")
    logger.info(f"OpenAI Available: {ai_generator.available}")
    
    app.run(
        host=AI_SERVICE_HOST,
        port=AI_SERVICE_PORT,
        debug=False
    )
