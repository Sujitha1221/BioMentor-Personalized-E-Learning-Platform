import pytest
from evaluate_answers import evaluate_answer_hybrid

def test_evaluate_answer_hybrid_typical_case():
    user_answer = "Photosynthesis uses sunlight, water and carbon dioxide to make glucose."
    model_answer = "Photosynthesis is a process where plants use sunlight, water, and carbon dioxide to produce glucose and oxygen."

    result = evaluate_answer_hybrid(user_answer, model_answer, "structured")


    assert "final_score" in result
    assert 0 <= result["final_score"] <= 100
    assert "semantic_score" in result
    assert isinstance(result["feedback"], dict)
