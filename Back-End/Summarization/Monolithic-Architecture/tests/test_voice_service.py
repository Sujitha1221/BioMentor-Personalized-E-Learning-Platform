from io import BytesIO
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from voice_service import text_to_speech

def test_text_to_speech():
    buffer = BytesIO()
    text_to_speech("Hello world", buffer)
    assert buffer.getvalue() != b""
