import logging
import os
from fastapi import UploadFile
import os
from io import BytesIO
from fpdf import FPDF


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

UPLOAD_DIR = "uploads"


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


def generate_pdf(structured_notes: str, topic: str) -> bytes:
    """
    Generate a PDF in English only using FPDF, returning the PDF data as bytes.

    :param structured_notes: The textual content for the PDF.
    :param topic: Title/topic for the PDF.
    :return: The PDF file data in bytes.
    """
    pdf = FPDF()
    pdf.add_page()

    # Set a title font (bold, size 16)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, txt=f"{topic}", ln=True, align="C")

    # Change to a normal font for content
    pdf.set_font("Arial", size=12)

    # Ensure proper UTF-8 encoding for special characters
    structured_notes = structured_notes.encode(
        "utf-8", "ignore").decode("utf-8")

    # Write multi-line text; FPDF's multi_cell wraps text automatically
    for line in structured_notes.split("\n"):
        pdf.multi_cell(0, 10, txt=line, align="L")

    # Generate the PDF in-memory properly
    pdf_bytes = pdf.output(dest='S').encode('latin1')  # Correct encoding

    return pdf_bytes
