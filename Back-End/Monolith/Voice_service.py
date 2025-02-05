import logging
import pyttsx3

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def text_to_speech(text, output_path):
    """
    Convert text to speech and save it to an audio file.
    """
    try:
        engine = pyttsx3.init()
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        logging.info(f"Voice file saved successfully: {output_path}")
    except Exception as e:
        logging.error(f"Failed to convert text to speech: {e}")
        raise RuntimeError("Error in text-to-speech conversion.")
