import os
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from datetime import datetime

from exam_practice import (
    get_one_sample_question,
    select_questions_per_student,
    get_questions_by_student_id,
    replace_question_for_student,
    compare_with_passpaper_answer
)

# ---------- MOCK DATA ----------
mock_student_id = "test123"
mock_structured_question = {
    "Question": "What is photosynthesis?",
    "Answer": "Photosynthesis is the process by which green plants make food.",
    "Type": "Structure"
}
mock_essay_question = {
    "Question": "Explain the process of respiration in humans.",
    "Answer": "Respiration is the metabolic process that converts glucose into energy in the presence of oxygen.",
    "Type": "Essay"
}


# ---------- TEST CASES ----------
@patch("exam_practice.df")
def test_get_one_sample_question(mock_df):
    sample_df = pd.DataFrame([
        {
            "Type": "Structure",
            "Question": "What is photosynthesis?",
            "Answer": "Photosynthesis is the process by which green plants make food."
        },
        {
            "Type": "Essay",
            "Question": "Explain the process of respiration in humans.",
            "Answer": "Respiration converts glucose into energy in presence of oxygen."
        }
    ])

    mock_df.__getitem__.side_effect = sample_df.__getitem__
    mock_df.sample.side_effect = sample_df.sample
    mock_df.__len__.side_effect = sample_df.__len__

    result = get_one_sample_question()
    
    assert "Structured_Question" in result
    assert "Essay_Question" in result
    assert isinstance(result["Structured_Question"], dict)
    assert isinstance(result["Essay_Question"], dict)


@patch("exam_practice.collection.insert_one")
@patch("exam_practice.get_one_sample_question")
def test_select_questions_per_student(mock_sample, mock_insert):
    mock_sample.return_value = {
        "Structured_Question": mock_structured_question,
        "Essay_Question": mock_essay_question
    }

    result = select_questions_per_student(mock_student_id)
    assert result["Student_ID"] == mock_student_id
    assert "Structured_Question" in result
    assert "Essay_Question" in result


@patch("exam_practice.collection.find_one")
@patch("exam_practice.select_questions_per_student")
def test_get_questions_by_student_id(mock_select, mock_find):
    mock_record = {
        "Student_ID": mock_student_id,
        "Structured_Question": mock_structured_question,
        "Essay_Question": mock_essay_question,
        "Assigned_Date": datetime.utcnow()
    }
    mock_find.return_value = mock_record

    result = get_questions_by_student_id(mock_student_id)
    assert "Structured_Question" in result
    assert "Essay_Question" in result


@patch("exam_practice.collection.find_one")
@patch("exam_practice.collection.update_one")
@patch("exam_practice.df")
def test_replace_question_for_student(mock_df, mock_update, mock_find):
    mock_find.return_value = {"Student_ID": mock_student_id}
    mock_df.__getitem__.return_value.sample.return_value.iloc.__getitem__.return_value = {
        "Question": "New Question",
        "Answer": "New Answer"
    }

    result = replace_question_for_student(mock_student_id, "structured")
    assert "Updated_Question" in result
    assert result["Student_ID"] == mock_student_id


@patch("exam_practice.replace_question_for_student")
@patch("exam_practice.save_evaluation")
@patch("exam_practice.evaluate_answer_hybrid")
@patch("exam_practice.collection.find_one")
def test_compare_with_passpaper_answer(mock_find, mock_eval, mock_save, mock_replace):
    mock_find.return_value = {
        "Structured_Question": {
            "Answer": "Correct structured answer."
        }
    }
    mock_eval.return_value = {
        "final_score": 88.0,
        "semantic_score": 90.0,
        "jaccard_score": 80.0,
        "grammar_score": 85.0,
        "feedback": {}
    }

    result = compare_with_passpaper_answer(mock_student_id, "What is the structure of DNA?", "DNA is double helix.", "structured")
    assert result["question_type"] == "structured"
    assert "evaluation_result" in result
