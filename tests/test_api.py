import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Rate Limiter API is running"

def test_fixed_window_allows():
    response = client.post("/fixed/testuser_fw")
    assert response.status_code == 200
    assert response.json()["status"] == "allowed"

def test_sliding_window_allows():
    response = client.post("/sliding/testuser_sw")
    assert response.status_code == 200
    assert response.json()["status"] == "allowed"

def test_token_bucket_allows():
    response = client.post("/token/testuser_tb")
    assert response.status_code == 200
    assert response.json()["status"] == "allowed"

def test_fixed_window_blocks_after_limit():
    for _ in range(5):
        client.post("/fixed/blocktest_fw")
    response = client.post("/fixed/blocktest_fw")
    assert response.status_code == 429

def test_stats_endpoint():
    client.post("/fixed/statsuser")
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_requests" in data
    assert "total_allowed" in data
    assert "total_blocked" in data

def test_user_stats_endpoint():
    client.post("/fixed/alice_stats")
    response = client.get("/stats/alice_stats")
    assert response.status_code == 200
    data = response.json()
    assert data["user"] == "alice_stats"
    assert data["allowed"] >= 1

def test_user_stats_not_found():
    response = client.get("/stats/nobody_xyz")
    assert response.status_code == 404