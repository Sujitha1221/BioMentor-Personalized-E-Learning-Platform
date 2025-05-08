import logging
from gtts import gTTS

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")


def text_to_speech(text, output_buffer):
    """
    Convert text to speech using gTTS and save it to an in-memory buffer.

    Args:
        text (str): Text to convert into speech.
        output_buffer (io.BytesIO): The buffer to store the MP3 file.
    """
    try:
        # Generate speech from text
        tts = gTTS(text, lang="en")

        # Save to buffer instead of file
        tts.write_to_fp(output_buffer)

        # Move buffer cursor to the beginning
        output_buffer.seek(0)

        logging.info("Voice file generated successfully in memory.")

    except Exception as e:
        logging.error(f"Failed to convert text to speech: {e}", exc_info=True)
        raise RuntimeError("Error in text-to-speech conversion.")
