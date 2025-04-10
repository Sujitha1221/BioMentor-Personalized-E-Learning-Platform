import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from bson import ObjectId
from question_and_answer_api import app

client = TestClient(app)


def test_root_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Question and Answer API is running!"}


@patch("generate_answers.generate_structured_answer", return_value="Structured answer here.")
@patch("predict_question_acceptability.moderate_question", return_value=(True, "OK"))
@patch("question_and_answer_api.get_related_websites", return_value=["https://example.com"])
@patch("question_and_answer_api.check_user_availability", return_value=(True, "User found."))
def test_generate_structured_answer(mock_user, mock_web, mock_mod, mock_gen):
    payload = {
        "student_id": "sajeesiva06@gmail.com",
        "question": "What is osmosis?",
        "type": "structured"
    }
    response = client.post("/generate-answer", json=payload)
    assert response.status_code == 200
    assert "answer" in response.json()


@patch("generate_answers.generate_essay_answer", return_value="Essay answer here.")
@patch("predict_question_acceptability.moderate_question", return_value=(True, "OK"))
@patch("question_and_answer_api.get_related_websites", return_value=["https://example.com"])
@patch("question_and_answer_api.check_user_availability", return_value=(True, "User found."))
def test_generate_essay_answer(mock_user, mock_web, mock_mod, mock_gen):
    payload = {
        "student_id": "sajeesiva06@gmail.com",
        "question": "Explain the process of digestion in humans.",
        "type": "essay"
    }
    response = client.post("/generate-answer", json=payload)
    assert response.status_code == 200
    assert "answer" in response.json()


@patch("question_and_answer_api.evaluate_user_answer")
@patch("predict_question_acceptability.moderate_question", return_value=(True, "OK"))
@patch("question_and_answer_api.get_related_websites", return_value=["https://example.com"])
@patch("question_and_answer_api.check_user_availability", return_value=(True, "User found."))
def test_evaluate_answer(mock_user, mock_web, mock_mod, mock_eval):
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
@patch("question_and_answer_api.convert_objectid")
@patch("question_and_answer_api.check_user_availability", return_value=(True, "User found."))
def test_student_analytics(mock_user, mock_convert, mock_analytics):
    # Sample data with ObjectId replaced by a string
    raw_data = {
        "_id": ObjectId("507f1f77bcf86cd799439011"),  # Simulating
        "evaluations": [],
        "average_scores": {},
        "score_trends": {},
        "feedback_report": {},
        "recommendations": {},
        "group_analysis": {},
        "class_average": {},
        "matched_study_materials": []
    }

    # 🛠 Mock get_student_analytic_details to return raw ObjectId-containing data
    mock_analytics.return_value = raw_data

    # 🛠 Mock convert_objectid to return a version with stringified ObjectId
    mock_convert.return_value = {
        "_id": str(raw_data["_id"]),
        "evaluations": [],
        "average_scores": {},
        "score_trends": {},
        "feedback_report": {},
        "recommendations": {},
        "group_analysis": {},
        "class_average": {},
        "matched_study_materials": []
    }

    response = client.post("/student-analytics", json={"student_id": "sajeesiva06@gmail.com"})
    assert response.status_code == 200
    assert response.json()["status"] == "success"

@patch("exam_practice.get_questions_by_student_id")
@patch("question_and_answer_api.check_user_availability", return_value=(True, "User found."))
def test_get_student_question(mock_user, mock_get):
    mock_get.return_value = {
        "Structured_Question": {"Question": "Define cell.", "Answer": "Basic unit of life."},
        "Essay_Question": {"Question": "Explain respiration.", "Answer": "Breakdown of glucose."},
        "Assigned_Date": "2024-03-25T00:00:00Z"
    }

    response = client.get("/get-student-question/stu001")
    assert response.status_code == 200
    assert "questions" in response.json()
