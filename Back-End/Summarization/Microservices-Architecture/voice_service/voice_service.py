import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from text_to_speech import text_to_speech

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()

class TTSRequest(BaseModel):
    text: str
    file_path: str

@app.post("/synthesize/")
async def synthesize_voice(request: TTSRequest):
    """
    Convert text to speech and save as an audio file.
    """
    try:
        logging.info(f"Received text-to-speech request. Saving to: {request.file_path}")
        
        # Pass the file path to text_to_speech
        text_to_speech(request.text, request.file_path)
        
        logging.info(f"Text-to-speech conversion successful. Audio file saved at: {request.file_path}")
        return {"audio_file": request.file_path}
    
    except Exception as e:
        logging.error(f"Text-to-speech conversion failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Text-to-speech conversion failed."
        )

if __name__ == "__main__":
    logging.info("Starting Voice Service on port 8003")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
