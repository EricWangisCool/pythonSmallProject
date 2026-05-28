import os
from flask import Blueprint, render_template, jsonify, send_from_directory, abort, request

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

@bp.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload to S3 and return a presigned download URL.
    Expects multipart/form-data with a field named 'file'.
    """
    from .s3_client import upload_file_to_s3, generate_presigned_download_url
    import os
    # Load bucket name from environment (via dotenv)
    bucket_name = os.getenv('S3_BUCKET_NAME')
    if not bucket_name:
        return jsonify({'error': 'S3 bucket name not configured'}), 500
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request'}), 400
    file_obj = request.files['file']
    if file_obj.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    # Use a safe object name (could prefix with user id etc.)
    object_name = file_obj.filename
    success = upload_file_to_s3(file_obj, bucket_name, object_name)
    if not success:
        return jsonify({'error': 'Failed to upload to S3'}), 500
    url = generate_presigned_download_url(bucket_name, object_name)
    if not url:
        return jsonify({'error': 'Failed to generate download URL'}), 500
    return jsonify({'download_url': url}), 200

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

