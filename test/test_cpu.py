import pytest
from src import create_app

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app({"TESTING": True})
    yield app
    # Cleanup after test runs to ensure no leftover CPU loader processes
    from src.cpu_manager import cpu_manager
    cpu_manager.stop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

def test_initial_status(client):
    """Test that the initial status of the CPU generator is idle."""
    response = client.get("/api/cpu/status")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["running"] is False
    assert json_data["target_percentage"] == 0
    assert json_data["process_count"] == 0
    assert "system_cpu" in json_data
    assert "num_cores" in json_data

def test_start_cpu_success(client):
    """Test starting CPU load with a valid percentage."""
    # Start at 5%
    response = client.post("/api/cpu/start", json={"percentage": 5})
    assert response.status_code == 200
    
    json_data = response.get_json()
    assert "Successfully started" in json_data["message"]
    assert json_data["status"]["running"] is True
    assert json_data["status"]["target_percentage"] == 5
    assert json_data["status"]["process_count"] > 0

    # Verify status endpoint reflects running state
    status_response = client.get("/api/cpu/status")
    status_data = status_response.get_json()
    assert status_data["running"] is True
    assert status_data["target_percentage"] == 5

def test_start_cpu_invalid_values(client):
    """Test starting CPU load with various invalid inputs."""
    # Negative percentage
    resp = client.post("/api/cpu/start", json={"percentage": -10})
    assert resp.status_code == 400
    assert "Percentage must be between 0 and 100" in resp.get_json()["error"]

    # Over 100%
    resp = client.post("/api/cpu/start", json={"percentage": 105})
    assert resp.status_code == 400
    assert "Percentage must be between 0 and 100" in resp.get_json()["error"]

    # Missing field
    resp = client.post("/api/cpu/start", json={})
    assert resp.status_code == 400
    assert "Percentage is required" in resp.get_json()["error"]

    # Non-integer percentage
    resp = client.post("/api/cpu/start", json={"percentage": "invalid"})
    assert resp.status_code == 400
    assert "Percentage must be an integer" in resp.get_json()["error"]

def test_stop_cpu(client):
    """Test stopping the CPU load generator resets status."""
    # Start it first
    client.post("/api/cpu/start", json={"percentage": 10})
    
    # Verify running
    status_resp = client.get("/api/cpu/status")
    assert status_resp.get_json()["running"] is True

    # Stop it
    stop_resp = client.post("/api/cpu/stop")
    assert stop_resp.status_code == 200
    assert "Successfully stopped" in stop_resp.get_json()["message"]

    # Verify idle again
    status_resp = client.get("/api/cpu/status")
    status_data = status_resp.get_json()
    assert status_data["running"] is False
    assert status_data["target_percentage"] == 0
    assert status_data["process_count"] == 0
