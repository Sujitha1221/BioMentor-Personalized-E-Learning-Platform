import logging
import logging.config
import yaml
from rag import RAGModel
from text_extraction_service import extract_content, clean_text, format_as_paragraph
from voice_service import text_to_speech
from file_handler import save_uploaded_file
import os
import io
import hashlib
from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware


# Load logging configuration
with open("logging_config.yaml", "r") as file:
    config = yaml.safe_load(file)
    logging.config.dictConfig(config)

logger = logging.getLogger("myapp")

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change this for production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG Model
try:
    logger.info("Initializing RAG Model...")
    rag_model = RAGModel(
        model_path='D:/Downloads/RP/Summarization/flan_t5_finetuned_model',
        embedding_model_name='all-MiniLM-L6-v2',
        dataset_paths=[
            '../../../Model-Training/Summarization/bio_summary_keywords.csv',
            '../../../Model-Training/Summarization/biology_information_retrieval_sample.csv'
        ]
    )
    logger.info("RAG Model initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize RAG Model: {e}", exc_info=True)
    raise

file_store = {}  # Temporary storage for files


@app.post("/process-document/")
async def process_document(file: UploadFile, word_count: int = Form(...)):
    """
    Process a document to extract, summarize, and generate a voice file.
    Returns appropriate responses based on processing status.
    """
    try:
        logger.info(f"Received document: {file.filename}. Processing...")

        # Save uploaded file
        file_path = save_uploaded_file(file)
        logger.info(f"File saved to {file_path}. Extracting content...")

        # Extract content
        raw_text = extract_content(file_path)
        if not raw_text.strip():
            logger.warning(f"No content extracted from {file.filename}.")
            raise HTTPException(
                status_code=400, detail="No content could be extracted from the document.")

        # Clean and format text
        cleaned_text = clean_text(raw_text)
        formatted_text = format_as_paragraph(cleaned_text)

        # Generate summary
        logger.info(f"Generating summary for {file.filename}...")
        summary = rag_model.generate_summary_for_long_text(
            formatted_text, max_words=word_count)

        if not summary:
            logger.warning(f"Failed to generate summary for {file.filename}.")
            raise HTTPException(
                status_code=500, detail="Summary generation failed.")

        # Generate dynamic filenames
        summary_file_path = file_path.rsplit(".", 1)[0] + "_summary.txt"
        audio_file_path = file_path.rsplit(".", 1)[0] + ".mp3"

        # Save summary in memory
        summary_bytes = summary.encode("utf-8")
        file_store["last_summary_file"] = summary_file_path
        file_store["last_audio_file"] = audio_file_path
        file_store[summary_file_path] = summary_bytes
        logger.info(f"Summary saved as {summary_file_path}.")

        # Generate audio file
        logger.info(f"Generating audio for {file.filename}...")
        audio_file = io.BytesIO()
        text_to_speech(summary, audio_file)
        audio_file.seek(0)
        file_store[audio_file_path] = audio_file.read()
        logger.info(f"Audio file saved as {audio_file_path}.")

        # Return response with file download links
        return {
            "summary": summary,
            "summary_file": "/download-summary-text/",
            "voice_file": "/download-summary-audio/"
        }

    except HTTPException as http_err:
        raise http_err  # Return FastAPI HTTPException directly

    except Exception as e:
        logger.error(
            f"Error processing document {file.filename}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to process document.")


@app.post("/process-query/")
async def process_query(query: str = Form(...), word_count: int = Form(...)):
    """
    Retrieve and summarize content based on a query and return results as an API response.
    """
    try:
        logger.info(f"Processing query: {query}")

        # Step 1: Check for inappropriate content
        inappropriate_message = rag_model.contains_inappropriate_content(query)
        if inappropriate_message:
            logger.warning(f"Inappropriate content detected: {query}")
            raise HTTPException(status_code=400, detail=inappropriate_message)

        # Step 2: Retrieve relevant content
        relevant_texts = rag_model.retrieve_relevant_content(query)

        if isinstance(relevant_texts, str) and "error" in relevant_texts.lower():
            logger.warning(
                f"Error retrieving relevant content: {relevant_texts}")
            raise HTTPException(
                status_code=500, detail="Error retrieving relevant content.")

        if not relevant_texts or relevant_texts == "No relevant content found":
            logger.warning(f"No relevant content found for query: {query}")
            raise HTTPException(
                status_code=404, detail="No relevant content found for the given query.")

        # Step 3: Generate Summary
        combined_text = " ".join(relevant_texts)
        summary = rag_model.generate_summary_for_long_text(
            combined_text, max_words=word_count)

        if not summary.strip():
            logger.warning(f"Generated summary is empty for query: {query}")
            raise HTTPException(
                status_code=500, detail="Failed to generate a summary.")

        # Step 4: Generate stable filenames using SHA-256 hash
        query_hash = hashlib.sha256(query.encode()).hexdigest()[:10]
        summary_file_path = f"query_summary_{query_hash}.txt"
        audio_file_path = f"query_audio_{query_hash}.mp3"

        # Store summary text file
        file_store["last_summary_file"] = summary_file_path
        file_store[summary_file_path] = summary.encode("utf-8")
        logger.info(f"Query summary saved as {summary_file_path}.")

        # Step 5: Convert summary to audio
        audio_file = io.BytesIO()
        text_to_speech(summary, audio_file)
        audio_file.seek(0)
        file_store["last_audio_file"] = audio_file_path
        file_store[audio_file_path] = audio_file.read()
        logger.info(f"Query audio saved as {audio_file_path}.")

        # Step 6: Return API Response
        return {
            "status": "success",
            "message": "Query processed successfully.",
            "summary": summary,
            "summary_file": f"/download-summary-text/{summary_file_path}",
            "voice_file": f"/download-summary-audio/{audio_file_path}"
        }

    except HTTPException as http_err:
        raise http_err  # Re-raise FastAPI errors with correct status codes

    except Exception as e:
        logger.error(f"Unexpected error processing query: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="An unexpected error occurred while processing the query.")


@app.post("/summarize-text/")
async def summarize_text(text: str = Form(...), word_count: int = Form(...)):
    """
    Summarizes a long text input and provides separate endpoints to download files.
    """
    try:
        logger.info("Received request to summarize text.")

        if not text.strip():
            logger.warning("Empty text input received.")
            raise HTTPException(
                status_code=400, detail="Text input cannot be empty.")

        # Check if the text contains inappropriate content
        inappropriate_response = RAGModel.contains_inappropriate_content(text)
        if inappropriate_response:
            return {"error": inappropriate_response}

        # Generate summary
        summary = rag_model.generate_summary_for_long_text(
            text, max_words=word_count)

        if not summary.strip():
            logger.warning("Generated summary is empty.")
            raise HTTPException(
                status_code=400, detail="Generated summary is empty.")

        # Generate file paths
        summary_file_path = "summary.txt"
        audio_file_path = "summary.mp3"

        # Store summary in memory
        file_store["last_summary_file"] = summary_file_path
        file_store["last_audio_file"] = audio_file_path
        file_store[summary_file_path] = summary.encode("utf-8")

        logger.info(
            f"Text summary saved as {summary_file_path}. Generating audio...")

        # Convert text to speech
        audio_file = io.BytesIO()
        text_to_speech(summary, audio_file)
        audio_file.seek(0)
        file_store[audio_file_path] = audio_file.read()

        logger.info(
            f"Audio file saved as {audio_file_path}. Summary processing complete.")

        return {
            "status": "success",
            "message": "Summary generated successfully.",
            "summary": summary,
            "summary_file": "/download-summary-text/",
            "voice_file": "/download-summary-audio/"
        }

    except HTTPException as http_error:
        raise http_error  # Return FastAPI HTTPException directly

    except Exception as e:
        logger.error(f"Error summarizing text: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Internal server error. Failed to summarize text.")


@app.get("/download-summary-text/")
async def download_summary_text():
    """Endpoint to download the last generated summary text file."""
    if "last_summary_file" not in file_store:
        logger.warning(
            "Download summary text request failed: No summary file found.")
        raise HTTPException(status_code=404, detail="No summary file found.")

    summary_file_path = file_store["last_summary_file"]

    if summary_file_path not in file_store:
        logger.warning(
            f"Summary file {summary_file_path} not found in storage.")
        raise HTTPException(status_code=404, detail="Summary file not found.")

    logger.info(f"Downloading summary file: {summary_file_path}")
    return StreamingResponse(io.BytesIO(file_store[summary_file_path]),
                             media_type="text/plain",
                             headers={"Content-Disposition": f"attachment; filename={os.path.basename(summary_file_path)}"})


@app.get("/download-summary-audio/")
async def download_summary_audio():
    """Endpoint to download the last generated summary audio file."""
    if "last_audio_file" not in file_store:
        logger.warning(
            "Download summary audio request failed: No audio file found.")
        raise HTTPException(status_code=404, detail="No audio file found.")

    audio_file_path = file_store["last_audio_file"]

    if audio_file_path not in file_store:
        logger.warning(f"Audio file {audio_file_path} not found in storage.")
        raise HTTPException(status_code=404, detail="Audio file not found.")

    logger.info(f"Downloading audio file: {audio_file_path}")
    return StreamingResponse(io.BytesIO(file_store[audio_file_path]),
                             media_type="audio/mpeg",
                             headers={"Content-Disposition": f"attachment; filename={os.path.basename(audio_file_path)}"})


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
