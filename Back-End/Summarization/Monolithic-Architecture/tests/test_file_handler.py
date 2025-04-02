import pytest
from fastapi import UploadFile
from io import BytesIO
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from file_handler import save_uploaded_file, generate_pdf

def test_save_uploaded_file(tmp_path):
    dummy_content = b"Hello, this is test content."
    file = UploadFile(filename="test.txt", file=BytesIO(dummy_content))
    path = save_uploaded_file(file)
    assert os.path.exists(path)
    os.remove(path)  # Clean up

def test_generate_pdf():
    content = "Line 1\nLine 2"
    title = "Test PDF"
    result = generate_pdf(content, title)
    assert isinstance(result, bytes)
    assert result.startswith(b"%PDF")


