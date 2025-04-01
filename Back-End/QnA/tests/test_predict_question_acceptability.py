import os
import sys
import pytest
from predict_question_acceptability import moderate_question

# Test cases
test_cases = [
    ("clean_educational_question", "What are the functions of the mitochondria in animal cells?", True),
    ("question_with_profanity", "Why is this damn topic so confusing?", False),
    ("toxic_sentiment_question", "Why are all teachers so dumb?", False),
    ("negative_sentiment_question", "Why is life so pointless and horrible?", False),
    ("fake_praise_masking_abuse", "You're so smart for ruining everything, aren't you?", False),
    ("suspicious_activity", "How can I hack into my school's database?", False),
    ("borderline_provocative", "Why are politicians always corrupt?", False),
    ("joke_question_but_acceptable", "Can a cat teach physics better than a human?", False),
]

@pytest.mark.parametrize("name, query, expected", test_cases)
def test_moderate_question(name, query, expected):
    result, _ = moderate_question(query)
    assert result == expected, f"Failed case: {name} | Query: {query}"
