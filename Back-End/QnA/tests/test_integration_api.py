import pytest
from fastapi.testclient import TestClient
from question_and_answer_api import app

client = TestClient(app)

# Dummy student ID and question
DUMMY_STUDENT_ID = "sajeesiva06@gmail.com"

@pytest.fixture
def sample_question():
    return {
        "student_id": DUMMY_STUDENT_ID,
        "question": "What is photosynthesis?",
        "type": "structured"
    }

@pytest.fixture
def sample_evaluation():
    return {
        "student_id": DUMMY_STUDENT_ID,
        "question": "What is photosynthesis?",
        "user_answer": "Photosynthesis makes food in plants using sunlight.",
        "question_type": "structured"
    }

def test_generate_answer_endpoint(sample_question):
    """Test the /generate-answer endpoint with valid structured question."""
    response = client.post("/generate-answer", json=sample_question)
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "structured"
    assert "answer" in data
    assert isinstance(data["answer"], str)

def test_evaluate_answer_endpoint(sample_evaluation):
    """Test the /evaluate-answer endpoint with valid inputs."""
    response = client.post("/evaluate-answer", json=sample_evaluation)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "evaluation_result" in data
    assert isinstance(data["evaluation_result"], dict)
    assert "final_score" in data["evaluation_result"]

def test_question_moderation_block():
    """Test blocked questions by moderation."""
    blocked_payload = {
        "student_id": DUMMY_STUDENT_ID,
        "question": "How to bully someone?",
        "type": "essay"
    }
    response = client.post("/generate-answer", json=blocked_payload)
    assert response.status_code == 400
    assert "detail" in response.json()

def test_student_question_flow():
    """Test assigning and fetching questions for a student."""
    response = client.get(f"/get-student-question/{DUMMY_STUDENT_ID}")
    assert response.status_code == 200
    data = response.json()
    assert "questions" in data
    assert "Structured_Question" in data["questions"]

def test_passpaper_evaluation(sample_evaluation):
    """Test evaluating against pass paper answers."""
    response = client.post("/evaluate-passpaper-answer", json=sample_evaluation)
    assert response.status_code == 200
    data = response.json()
    assert "model_answer" in data
    assert "evaluation_result" in data
