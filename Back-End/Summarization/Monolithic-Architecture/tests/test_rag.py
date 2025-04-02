import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from rag import RAGModel

class DummyModel:
    def generate_summary_for_long_text(self, text, max_words=100):
        return "summary"

def test_truncate_to_word_count():
    text = "This is a test sentence. " * 50
    model = DummyModel()
    result = RAGModel.truncate_to_word_count(text, max_words=20)
    assert len(result.split()) <= 20

def test_postprocess_summary():
    summary = "this is a test. this is another sentence."
    model = DummyModel()
    result = RAGModel.postprocess_summary(model, summary)
    assert result[0].isupper()
    assert result.endswith(".")
