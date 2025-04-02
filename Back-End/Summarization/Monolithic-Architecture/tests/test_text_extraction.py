import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from text_extraction_service import clean_text, format_as_paragraph, find_errors, resolve_errors

def test_clean_text():
    dirty_text = "  This    is     a test   ."
    cleaned = clean_text(dirty_text)
    assert "  " not in cleaned
    assert cleaned.endswith(".")

def test_format_as_paragraph():
    text = "This is line one.\nThis is line two."
    result = format_as_paragraph(text)
    assert "\n" not in result
    assert ". " in result

def test_find_and_resolve_errors():
    text = "Double.. punctuation!! here??"
    errors = find_errors(text)
    assert "Double punctuation" in errors

