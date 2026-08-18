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
    for _ in range(10):
        client.post("/fixed/blocktest_fw")
    response = client.post("/fixed/blocktest_fw")
    assert response.status_code == 429
    assert response.json()["detail"] == "Too Many Requests"

def test_metrics_endpoint():
    client.post("/fixed/metrics_user")
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "ratekeep_requests_total" in response.text