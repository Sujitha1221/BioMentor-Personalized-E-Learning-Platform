import sys
import os
from bson import ObjectId

# Dynamically add the absolute path to project root (MCQ) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

dummy_user_id = str(ObjectId())

from utils.quiz_generation_methods import (
    assign_difficulty_parameter,
    assign_discrimination_parameter,
    get_irt_based_difficulty_distribution
)

def test_assign_difficulty_parameter_easy_range():
    value = assign_difficulty_parameter(dummy_user_id, "easy")
    assert -2.0 <= value <= 1.0

def test_assign_difficulty_parameter_hard_range():
    value = assign_difficulty_parameter(dummy_user_id, "hard")
    assert isinstance(value, float)

def test_assign_discrimination_parameter_range():
    value = assign_discrimination_parameter()
    assert 0.5 <= value <= 2.0

def test_get_irt_based_difficulty_distribution_low_theta():
    distribution = get_irt_based_difficulty_distribution(dummy_user_id, 10)
    assert sum(distribution.values()) == 10
    assert isinstance(distribution, dict)

def test_get_irt_based_difficulty_distribution_high_theta():
    distribution = get_irt_based_difficulty_distribution(dummy_user_id, 10)
    assert sum(distribution.values()) == 10
    assert isinstance(distribution, dict)