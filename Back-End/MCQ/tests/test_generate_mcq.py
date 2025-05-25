import sys
import os
import pandas as pd
import numpy as np
from unittest.mock import patch
from bson import ObjectId

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import utils.generate_question as gq
from utils.generate_question import generate_mcq, generate_mcq_based_on_performance

FAKE_RAW_OUTPUT = """
Question 1: What is the powerhouse of the cell?
A) Nucleus
B) Ribosome
C) Mitochondria
D) Golgi apparatus
E) Lysosome
Correct Answer: C
"""

def mock_extracted_mcq():
    return [{
        "question": "What is the powerhouse of the cell?",
        "options": {
            "A": "Nucleus",
            "B": "Ribosome",
            "C": "Mitochondria",
            "D": "Golgi apparatus",
            "E": "Lysosome"
        },
        "correct_answer": "C"
    }]

@patch("utils.generate_question.verify_mcq_with_llm", return_value=(True, "C", "C"))
@patch("utils.generate_question.extract_mcqs", return_value=mock_extracted_mcq())
@patch("utils.generate_question.index.add")
@patch("utils.generate_question.embedding_model.encode", return_value=np.array([[0.1]*384], dtype=np.float32))
@patch("utils.generate_question.retrieve_context_questions", return_value=pd.DataFrame())
def test_generate_mcq_success(mock_context, mock_encode, mock_add, mock_extract, mock_verify):
    mock_df = pd.DataFrame([{
        "Question Text": "What is the powerhouse of the cell?",
        "Correct Answer": "C",
        "Cluster": 1
    }])

    with patch.object(gq, "dataset", mock_df):
        result = generate_mcq("easy", str(ObjectId()), max_retries=1)

        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0]["difficulty"] == "easy"
        assert "question" in result[0]
        assert result[0]["is_verified"] is True
        assert result[0]["correct_answer"] == "C"

@patch("utils.generate_question.verify_mcq_with_llm", return_value=(True, "C", "C"))
@patch("utils.generate_question.extract_mcqs", return_value=mock_extracted_mcq())
@patch("utils.generate_question.index.add")
@patch("utils.generate_question.embedding_model.encode", return_value=np.array([[0.1]*384], dtype=np.float32))
@patch("utils.generate_question.retrieve_context_questions", return_value=pd.DataFrame())
@patch("utils.generate_question.estimate_student_ability", return_value=0.5)
def test_generate_mcq_based_on_performance_success(mock_theta, mock_context, mock_encode, mock_add, mock_extract, mock_verify):
    mock_df = pd.DataFrame([{
        "Question Text": "What is the powerhouse of the cell?",
        "Correct Answer": "C",
        "Cluster": 1
    }])

    with patch.object(gq, "dataset", mock_df):
        result = generate_mcq_based_on_performance(str(ObjectId()), "medium", max_retries=1)

        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0]["difficulty"] == "medium"
        assert "question" in result[0]
        assert result[0]["is_verified"] is True
        assert result[0]["correct_answer"] == "C"
