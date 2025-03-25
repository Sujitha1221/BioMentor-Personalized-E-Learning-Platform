import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from question_and_answer_api import app

client = TestClient(app)


def test_root_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Question and Answer API is running!"}


@patch("question_and_answer_api.moderate_question", return_value=(True, "OK"))
@patch("question_and_answer_api.generate_structured_answer", return_value="Structured answer here.")
@patch("question_and_answer_api.get_related_websites", return_value=["https://example.com"])
def test_generate_structured_answer(mock_web, mock_gen, mock_mod):
    payload = {
        "question": "What is osmosis?",
        "type": "structured"
    }
    response = client.post("/generate-answer", json=payload)
    assert response.status_code == 200
    assert "answer" in response.json()


@patch("question_and_answer_api.moderate_question", return_value=(True, "OK"))
@patch("question_and_answer_api.generate_essay_answer", return_value="Essay answer here.")
@patch("question_and_answer_api.get_related_websites", return_value=["https://example.com"])
def test_generate_essay_answer(mock_web, mock_gen, mock_mod):
    payload = {
        "question": "Explain the process of digestion in humans.",
        "type": "essay"
    }
    response = client.post("/generate-answer", json=payload)
    assert response.status_code == 200
    assert "answer" in response.json()


@patch("question_and_answer_api.moderate_question", return_value=(True, "OK"))
@patch("question_and_answer_api.evaluate_user_answer")
@patch("question_and_answer_api.get_related_websites", return_value=["https://example.com"])
def test_evaluate_answer(mock_web, mock_eval, mock_mod):
    mock_eval.return_value = {
        "question": "What is DNA?",
        "question_type": "structured",
        "user_answer": "DNA is genetic material.",
        "model_answer": "DNA stores genetic information.",
        "evaluation_result": {"final_score": 85}
    }

    payload = {
        "student_id": "stu123",
        "question": "What is DNA?",
        "user_answer": "DNA is genetic material.",
        "question_type": "structured"
    }

    response = client.post("/evaluate-answer", json=payload)
    assert response.status_code == 200
    assert response.json()["evaluation_result"]["final_score"] == 85


@patch("question_and_answer_api.get_student_analytic_details")
def test_student_analytics(mock_analytics):
    mock_analytics.return_value = {
        "evaluations": [],
        "average_scores": {},
        "score_trends": {},
        "feedback_report": {},
        "recommendations": {},
        "group_analysis": {},
        "class_average": {},
        "matched_study_materials": []
    }

    response = client.post("/student-analytics", json={"student_id": "stu001"})
    assert response.status_code == 200
    assert response.json()["status"] == "success"


@patch("question_and_answer_api.get_questions_by_student_id")
def test_get_student_question(mock_get):
    mock_get.return_value = {
        "Structured_Question": {"Question": "Define cell.", "Answer": "Basic unit of life."},
        "Essay_Question": {"Question": "Explain respiration.", "Answer": "Breakdown of glucose."},
        "Assigned_Date": "2024-03-25T00:00:00Z"
    }

    response = client.get("/get-student-question/stu001")
    assert response.status_code == 200
    assert "questions" in response.json()
