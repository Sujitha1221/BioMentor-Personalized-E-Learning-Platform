import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.text_extraction import extract_mcqs
from utils.quiz_generation_methods import clean_correct_answer

def test_extract_mcqs_parsing_single_question():
    prompt = "Ignore this prompt."
    raw_output = """
    Question 1: What is the powerhouse of the cell?
    A) Nucleus
    B) Ribosome
    C) Mitochondria
    D) Chloroplast
    E) Endoplasmic Reticulum
    Correct Answer: C
    """
    parsed = extract_mcqs(prompt, raw_output)
    assert len(parsed) == 1
    assert parsed[0]["question"].startswith("What is")
    assert parsed[0]["correct_answer"] == "C"
    assert "A" in parsed[0]["options"]
    assert len(parsed[0]["options"]) == 5


@pytest.mark.parametrize("raw_input, expected", [
    ("Correct Answer: A", ["A"]),
    ("Answer: C and D", ["C", "D"]),
    ("B, D", ["B", "D"]),
    ("(E)", ["E"]),
    ("A, A, C", ["A", "C"]),
    ("123", []),
    ("", []),
    ("Correct Answer: A, C, E", ["A", "C", "E"]),
])
def test_clean_correct_answer_letters(raw_input, expected):
    assert clean_correct_answer(raw_input) == expected
