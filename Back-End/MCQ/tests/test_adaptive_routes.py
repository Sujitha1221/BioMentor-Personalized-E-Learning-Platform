
import pytest
from fastapi.testclient import TestClient
from main import app
from database.database import users_collection, quizzes_collection
from bson import ObjectId
from utils.user_mgmt_methods import get_current_user

TEST_USER_ID = "000000000000000000000003"

def override_get_current_user():
    return TEST_USER_ID

app.dependency_overrides[get_current_user] = override_get_current_user
client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_user():
    users_collection.insert_one({
        "_id": ObjectId(TEST_USER_ID),
        "username": "test_user",
        "performance": {
            "total_quizzes": 1,
            "accuracy_easy": 80,
            "accuracy_medium": 70,
            "accuracy_hard": 60,
            "time_easy": 5,
            "time_medium": 5,
            "time_hard": 5,
            "strongest_area": "easy",
            "weakest_area": "hard",
            "consistency_score": 90,
            "last_10_quizzes": [{
                "accuracy": 75,
                "total_time": 45,
                "timestamp": 1712724584.0
            }]
        }
    })
    yield
    users_collection.delete_many({"_id": ObjectId(TEST_USER_ID)})

def test_generate_mcqs():
    response = client.get(f"/generate_mcqs/{TEST_USER_ID}")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert "quiz_id" in data
        assert "mcqs" in data

def test_generate_adaptive_mcqs():
    response = client.get(f"/generate_adaptive_mcqs/{TEST_USER_ID}/5")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert "quiz_id" in data
        assert "mcqs" in data


def test_submit_quiz_and_get_quiz():
    # First generate quiz
    gen = client.get(f"/generate_mcqs/{TEST_USER_ID}")
    if gen.status_code != 200:
        pytest.skip("MCQ quiz not available for submission test")

    quiz_data = gen.json()
    quiz_id = quiz_data["quiz_id"]
    questions = quiz_data["mcqs"]

    # Submit fake answers
    submission_payload = {
        "user_id": TEST_USER_ID,
        "quiz_id": quiz_id,
        "responses": [
            {
                "question_text": q["question_text"],
                "selected_answer": "A",
                "time_taken": 3.0
            } for q in questions
        ]
    }
    submit = client.post("/submit_quiz/", json=submission_payload)
    assert submit.status_code == 200
    assert "summary" in submit.json()

    # Fetch quiz using the same quiz_id
    fetch = client.get(f"/get_quiz/{quiz_id}")
    assert fetch.status_code == 200
    assert fetch.json()["quiz_id"] == quiz_id
