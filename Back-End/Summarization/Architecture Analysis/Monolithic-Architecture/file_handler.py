import logging
import os
from fastapi import UploadFile
import os


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

UPLOAD_DIR = "/app/uploads" 

def save_uploaded_file(file: UploadFile):
    """
    Save an uploaded file to the uploads directory.
    """
    try:
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)
            logging.info(f"Created upload directory: {UPLOAD_DIR}")

        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        logging.info(f"File saved successfully: {file_path}")
        return file_path
    except Exception as e:
        logging.error(f"Failed to save uploaded file: {e}")
        raise RuntimeError("Error in saving uploaded file.")


