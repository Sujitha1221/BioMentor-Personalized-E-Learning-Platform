import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from text_extraction import extract_content

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()

UPLOAD_DIR = "/app/uploads"  # ✅ Ensure it matches API Gateway


class FilePathRequest(BaseModel):
    file_path: str

@app.post("/extract/")
async def extract_text(request: FilePathRequest):
    """
    Extract text from a given file.
    """
    try:
        logging.info(f"Received text extraction request for file: {request.file_path}")

        extracted_text = extract_content(request.file_path)
        if not extracted_text.strip():
            logging.warning(f"No text extracted from file: {request.file_path}")
            raise HTTPException(status_code=400, detail="No text extracted from the document.")

        logging.info(f"Text extraction successful for file: {request.file_path}")
        return {"text": extracted_text}

    except HTTPException as he:
        logging.error(f"Text extraction failed for {request.file_path}: {he.detail}")
        raise he

    except Exception as e:
        logging.error(f"Unexpected error during text extraction for {request.file_path}: {e}")
        raise HTTPException(status_code=500, detail="Failed to extract text.")

if __name__ == "__main__":
    logging.info("Starting Text Extraction Service on port 8001")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
