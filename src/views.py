import os
from flask import Blueprint, render_template, jsonify, send_from_directory, abort

bp = Blueprint("views", __name__)

IMAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "images"))
TEXT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "texts"))

@bp.route("/")
def index():
    """Render the landing page of the Flask application."""
    return render_template("index.html")

@bp.route("/api/health")
def health():
    """Health check endpoint for monitoring."""
    return jsonify({
        "status": "healthy",
        "service": "Flask Demo App",
        "port": 19191,
        "version": "1.0.0"
    })

@bp.route("/feature1/<picture_name>")
def feature1(picture_name):
    """Retrieve an image by name from the data/images directory."""
    try:
        return send_from_directory(IMAGE_DIR, picture_name)
    except FileNotFoundError:
        abort(404, description="Image not found")

@bp.route("/feature2/<file_name>")
def feature2(file_name):
    """Retrieve the text content of a txt file by name from the data/texts directory."""
    # Ensure secure path and prevent directory traversal
    safe_path = os.path.abspath(os.path.join(TEXT_DIR, file_name))
    if not safe_path.startswith(TEXT_DIR):
        abort(403, description="Access denied")
    
    if not os.path.isfile(safe_path) or not file_name.endswith(".txt"):
        abort(404, description="Text file not found")
        
    try:
        with open(safe_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content, 200, {"Content-Type": "text/plain; charset=utf-8"}
    except Exception:
        abort(500, description="Internal server error reading file")

