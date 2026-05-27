import pytest
from src import create_app

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app({"TESTING": True})
    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

def test_index_route(client):
    """Test that index page loads successfully."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Flask Application" in response.data
    assert b"Port 19191" in response.data

def test_health_api(client):
    """Test that the health endpoint returns correct JSON configuration."""
    response = client.get("/api/health")
    assert response.status_code == 200
    
    json_data = response.get_json()
    assert json_data["status"] == "healthy"
    assert json_data["service"] == "Flask Demo App"
    assert json_data["port"] == 19191
    assert json_data["version"] == "1.0.0"

def test_feature1_success(client):
    """Test that feature1 successfully returns an image."""
    response = client.get("/feature1/sample.png")
    assert response.status_code == 200
    assert response.mimetype == "image/png"

def test_feature1_not_found(client):
    """Test that feature1 returns 404 for a missing image."""
    response = client.get("/feature1/nonexistent.png")
    assert response.status_code == 404

def test_feature2_success(client):
    """Test that feature2 successfully returns text file content."""
    response = client.get("/feature2/sample.txt")
    assert response.status_code == 200
    assert b"Hello from Flask!" in response.data
    assert response.mimetype == "text/plain"

def test_feature2_not_found(client):
    """Test that feature2 returns 404 for a missing text file."""
    response = client.get("/feature2/nonexistent.txt")
    assert response.status_code == 404

def test_feature2_invalid_extension(client):
    """Test that feature2 returns 404 for a file that is not .txt."""
    response = client.get("/feature2/sample.png")
    assert response.status_code == 404

def test_directory_traversal_prevention(client):
    """Test that directory traversal attempts are blocked or return 404/403."""
    response = client.get("/feature2/../images/sample.png")
    assert response.status_code in (403, 404)

