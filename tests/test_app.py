import os

# Tests must not call Gemini.
os.environ["DEMO_MODE"] = "true"
os.environ["GEMINI_API_KEY"] = ""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_home_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "FitBuddy" in response.text
    assert "Create your plan" in response.text


def test_generate_workout_api():
    payload = {
        "username": "Test User",
        "user_id": "test_001",
        "age": 20,
        "weight": 60,
        "goal": "general wellness",
        "intensity": "medium",
    }

    response = client.post("/api/generate-workout", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["user_id"] == "test_001"
    assert "Day 1" in data["workout_plan"]
    assert data["source"] == "demo"
    assert data["nutrition_tip"]


def test_feedback_api():
    payload = {
        "user_id": "test_001",
        "feedback": "Add more mobility work and one rest day.",
    }

    response = client.post("/api/submit-feedback", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["user_id"] == "test_001"
    assert "UPDATED USING YOUR FEEDBACK" in data["updated_plan"]


def test_users_api():
    response = client.get("/api/users")
    assert response.status_code == 200
    assert any(user["user_id"] == "test_001" for user in response.json())


def test_invalid_age():
    payload = {
        "username": "Test User",
        "user_id": "invalid_age",
        "age": 12,
        "weight": 60,
        "goal": "general wellness",
        "intensity": "medium",
    }

    response = client.post("/api/generate-workout", json=payload)
    assert response.status_code == 422
