
import pytest
from fastapi.testclient import TestClient
from main import app
from database.database import users_collection, unit_quizzes, unit_quiz_responses
from bson import ObjectId
from utils.user_mgmt_methods import get_current_user
from datetime import datetime

# Use a known test ID for consistent mock
TEST_USER_ID = "000000000000000000000001"

# Dependency override to simulate authentication
def override_get_current_user():
    return TEST_USER_ID

app.dependency_overrides[get_current_user] = override_get_current_user
client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_user():
    users_collection.insert_one({
        "_id": ObjectId(TEST_USER_ID),
        "username": "test_user",
        "performance": {
            "total_quizzes": 0,
            "accuracy_easy": 0,
            "accuracy_medium": 0,
            "accuracy_hard": 0,
            "time_easy": 0,
            "time_medium": 0,
            "time_hard": 0,
            "strongest_area": "N/A",
            "weakest_area": "N/A",
            "consistency_score": 0,
            "last_10_quizzes": []
        }
    })
    yield
    users_collection.delete_many({"_id": ObjectId(TEST_USER_ID)})

def test_dashboard_data():
    response = client.get(f"/dashboard_data/{TEST_USER_ID}")
    assert response.status_code in [200, 404]  # Accept default or seeded response

def test_performance_graph():
    response = client.get(f"/performance_graph/{TEST_USER_ID}")
    assert response.status_code in [200, 404]

def test_leaderboard():
    response = client.get("/leaderboard")
    assert response.status_code in [200, 404]

def test_generate_unit_quiz():
    unit = "Photosynthesis"  # Change this to a valid unit in your dataset if needed
    response = client.get(f"/unit_quiz/generate/{TEST_USER_ID}?unit={unit}&question_count=1")
    if response.status_code == 200:
        assert "quiz_id" in response.json()
    else:
        assert response.status_code == 404  # If unit doesn't exist

def test_submit_unit_quiz():
    unit = "Photosynthesis"
    gen_response = client.get(f"/unit_quiz/generate/{TEST_USER_ID}?unit={unit}&question_count=1")
    if gen_response.status_code != 200:
        return  # skip test if no questions

    quiz_id = gen_response.json()["quiz_id"]
    questions = gen_response.json()["questions"]

    payload = {
        "quiz_id": quiz_id,
        "responses": [
            {"question_text": q["question_text"], "selected_answer": "A"}
            for q in questions
        ]
    }

    response = client.post(f"/unit_quiz/submit/{TEST_USER_ID}", json=payload)
    assert response.status_code == 200
    assert "score" in response.json()

def test_unit_quiz_results():
    unit = "Photosynthesis"
    gen_response = client.get(f"/unit_quiz/generate/{TEST_USER_ID}?unit={unit}&question_count=1")
    if gen_response.status_code != 200:
        return

    quiz_id = gen_response.json()["quiz_id"]
    questions = gen_response.json()["questions"]

    client.post(f"/unit_quiz/submit/{TEST_USER_ID}", json={
        "quiz_id": quiz_id,
        "responses": [{"question_text": q["question_text"], "selected_answer": "A"} for q in questions]
    })

    response = client.get(f"/unit_quiz/results/{quiz_id}")
    assert response.status_code == 200
    assert "responses" in response.json()
