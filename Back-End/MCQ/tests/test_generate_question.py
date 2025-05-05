import sys
import os
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

def test_clean_correct_answer_letters():
    assert clean_correct_answer("Correct Answer: A") == ["A"]
    assert clean_correct_answer("Answer: C and D") == ["C", "D"]
    assert clean_correct_answer("B, D") == ["B", "D"]
    assert clean_correct_answer("(E)") == ["E"]
    assert clean_correct_answer("A, A, C") == ["A", "C"]
    assert clean_correct_answer("123") == []
    assert clean_correct_answer("") == []
    assert clean_correct_answer("Correct Answer: A, C, E") == ["A", "C", "E"]  # ✅ this is the correct expectation

   
