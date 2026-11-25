from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_healthcheck():
    response = client.get("/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_assess_endpoint_approved():
    payload = {
        "applicant_id": "app-api-test-01",
        "age": 31,
        "annual_income": 60000.0,
        "monthly_debt_obligations": 400.0,
        "credit_score": 760,
        "requested_amount": 5000.0,
        "has_bankruptcies": False,
        "has_recent_ccj": False,
    }
    response = client.post("/v1/underwrite/assess", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "APPROVED"
    assert data["risk_tier"] == "TIER_A"
    assert data["approved_limit"] == 5000.0
    assert data["offered_apr"] == 14.9


def test_assess_endpoint_invalid_payload():
    payload = {
        "applicant_id": "x",  # min_length is 3
        "age": -5,
        "annual_income": -100.0,
        "monthly_debt_obligations": 0.0,
        "credit_score": 200,  # below 300
        "requested_amount": 0.0,
    }
    response = client.post("/v1/underwrite/assess", json=payload)
    assert response.status_code == 422
