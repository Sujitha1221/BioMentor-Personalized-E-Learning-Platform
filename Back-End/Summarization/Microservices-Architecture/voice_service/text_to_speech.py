import logging
from gtts import gTTS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def text_to_speech(text, output_path):
    """
    Convert text to speech using gTTS and save the MP3 to the specified file path.
    """
    try:
        # Generate speech from text
        tts = gTTS(text, lang="en")
        
        # Save directly to a file
        tts.save(output_path)

        logging.info(f"Voice file generated successfully at path: {output_path}")

    except Exception as e:
        logging.error(f"Failed to convert text to speech: {e}", exc_info=True)
        raise RuntimeError("Error in text-to-speech conversion.")
