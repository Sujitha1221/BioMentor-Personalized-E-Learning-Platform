import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Ensure the project root is in the import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from answer_evaluation_tool import (
    compute_average_scores,
    get_score_trends,
    generate_feedback_report,
    generate_recommendations,
    get_group_analysis,
    calculate_class_average,
)

mock_evaluations = [
    {
        "student_id": "student001",
        "question": "What is photosynthesis?",
        "evaluation_result": {
            "final_score": 80,
            "semantic_score": 85,
            "tfidf_score": 75,
            "jaccard_score": 70,
            "grammar_score": 90,
            "feedback": {
                "missing_keywords": ["glucose"],
                "extra_keywords": ["sunligt"],
                "grammar_suggestions": ["Replace 'sunligt' with 'sunlight'"]
            }
        },
        "timestamp": "2024-01-01T10:00:00Z"
    },
    {
        "student_id": "student001",
        "question": "Explain DNA structure.",
        "evaluation_result": {
            "final_score": 65,
            "semantic_score": 70,
            "tfidf_score": 60,
            "jaccard_score": 55,
            "grammar_score": 85,
            "feedback": {
                "missing_keywords": ["double helix"],
                "extra_keywords": [],
                "grammar_suggestions": []
            }
        },
        "timestamp": "2024-01-02T10:00:00Z"
    }
]


@patch("answer_evaluation_tool.get_student_evaluations")
def test_compute_average_scores(mock_get):
    mock_get.return_value = mock_evaluations
    result = compute_average_scores("student001")
    assert result["semantic_score"] > 0
    assert "grammar_score" in result


@patch("answer_evaluation_tool.get_student_evaluations")
def test_get_score_trends(mock_get):
    mock_get.return_value = mock_evaluations
    result = get_score_trends("student001")
    assert "timestamps" in result
    assert "scores" in result
    assert len(result["scores"]["semantic_score"]) == 2


@patch("answer_evaluation_tool.get_student_evaluations")
def test_generate_feedback_report(mock_get):
    mock_get.return_value = mock_evaluations
    result = generate_feedback_report("student001")
    assert "strengths" in result
    assert "weaknesses" in result
    assert isinstance(result["missing_keywords"], list)


@patch("answer_evaluation_tool.get_student_evaluations")
def test_generate_recommendations(mock_get):
    mock_get.return_value = mock_evaluations
    result = generate_recommendations("student001")
    assert "learning_path" in result
    assert "keyword_mastery" in result
    assert "weak" in result["keyword_mastery"]


@patch("answer_evaluation_tool.db")
def test_get_group_analysis(mock_db):
    mock_db["evaluations"].find.return_value = mock_evaluations
    result = get_group_analysis(["student001"])
    assert "average_scores" in result
    assert "total_evaluations" in result


@patch("answer_evaluation_tool.db")
def test_calculate_class_average(mock_db):
    mock_db["evaluations"].find.return_value = mock_evaluations
    result = calculate_class_average()
    assert "semantic_score" in result
    assert "total_students" in result
