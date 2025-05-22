import logging
from fastapi import FastAPI, UploadFile, HTTPException
from file_handler import save_uploaded_file

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()

@app.post("/upload/")
async def upload_file(file: UploadFile):
    """
    Save an uploaded file to the uploads directory.
    """
    try:
        logging.info(f"Received file upload request: {file.filename}")

        file_path = save_uploaded_file(file)

        logging.info(f"File {file.filename} successfully saved at {file_path}")
        return {"file_path": file_path}

    except Exception as e:
        logging.error(f"File upload failed for {file.filename}: {e}")
        raise HTTPException(status_code=500, detail="File upload failed.")

if __name__ == "__main__":
    import uvicorn
    logging.info("Starting File Upload Service on port 8004")
    uvicorn.run(app, host="0.0.0.0", port=8004)
