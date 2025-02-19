import logging
import logging.config
import yaml
from fastapi import FastAPI, UploadFile, Form, HTTPException, BackgroundTasks, Response
from fastapi.responses import StreamingResponse
from rag import RAGModel
from text_extraction_service import extract_content, clean_text, format_as_paragraph
from voice_service import text_to_speech
from file_handler import save_uploaded_file
import os
import io

# Load logging configuration
with open("logging_config.yaml", "r") as file:
    config = yaml.safe_load(file)
    logging.config.dictConfig(config)

logger = logging.getLogger("myapp")

app = FastAPI()

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
    Process a document to extract, summarize, and generate a voice file,
    then return the output files as API responses.
    """
    try:
        logger.info(f"Received document: {file.filename}. Processing...")
        file_path = save_uploaded_file(file)
        logger.info(f"File saved to {file_path}. Extracting content...")

        raw_text = extract_content(file_path)
        if not raw_text.strip():
            logger.warning(f"No content extracted from {file.filename}.")
            raise HTTPException(status_code=400, detail="No content could be extracted from the document.")

        cleaned_text = clean_text(raw_text)
        formatted_text = format_as_paragraph(cleaned_text)

        logger.info(f"Generating summary for {file.filename}...")
        summary = rag_model.generate_summary_for_long_text(formatted_text, max_words=word_count)

        # Generate dynamic filenames
        summary_file_path = file_path.rsplit(".", 1)[0] + "_summary.txt"
        audio_file_path = file_path.rsplit(".", 1)[0] + ".mp3"

        # Save summary in memory
        summary_bytes = summary.encode("utf-8")
        file_store["last_summary_file"] = summary_file_path
        file_store["last_audio_file"] = audio_file_path
        file_store[summary_file_path] = summary_bytes
        logger.info(f"Summary saved as {summary_file_path}.")

        # Generate voice file
        logger.info(f"Generating audio for {file.filename}...")
        audio_file = io.BytesIO()
        text_to_speech(summary, audio_file)
        audio_file.seek(0)
        file_store[audio_file_path] = audio_file.read()
        logger.info(f"Audio file saved as {audio_file_path}.")

        return {
            "summary": summary,
            "summary_file": "/download-summary-text/",
            "voice_file": "/download-summary-audio/"
        }
    except Exception as e:
        logger.error(f"Error processing document {file.filename}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process document.")

@app.post("/process-query/")
async def process_query(query: str = Form(...), word_count: int = Form(...)):
    """
    Retrieve and summarize content based on a query and return results as an API response.
    """
    try:
        logger.info(f"Processing query: {query}")

        relevant_texts = rag_model.retrieve_relevant_content(query)
        if not relevant_texts:
            logger.warning(f"No relevant content found for query: {query}")
            raise HTTPException(status_code=400, detail="No relevant content found for the given query.")

        combined_text = " ".join(relevant_texts)
        summary = rag_model.generate_summary_for_long_text(combined_text, max_words=word_count)

        # Generate dynamic filenames
        summary_file_path = f"query_summary_{hash(query)}.txt"
        audio_file_path = f"query_audio_{hash(query)}.mp3"

        file_store["last_summary_file"] = summary_file_path
        file_store["last_audio_file"] = audio_file_path
        file_store[summary_file_path] = summary.encode("utf-8")
        logger.info(f"Query summary saved as {summary_file_path}.")

        audio_file = io.BytesIO()
        text_to_speech(summary, audio_file)
        audio_file.seek(0)
        file_store[audio_file_path] = audio_file.read()
        logger.info(f"Query audio saved as {audio_file_path}.")

        return {
            "summary": summary,
            "summary_file": "/download-summary-text/",
            "voice_file": "/download-summary-audio/"
        }
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process query.")

@app.post("/summarize-text/")
async def summarize_text(text: str = Form(...), word_count: int = Form(...)):
    """
    Summarizes a long text input and provides separate endpoints to download files.
    """
    try:
        logger.info("Received request to summarize text.")

        if not text.strip():
            logger.warning("Empty text input received.")
            raise HTTPException(status_code=400, detail="Text input cannot be empty.")

        summary = rag_model.generate_summary_for_long_text(text, max_words=word_count)

        summary_file_path = "summary.txt"
        audio_file_path = "summary.mp3"

        file_store["last_summary_file"] = summary_file_path
        file_store["last_audio_file"] = audio_file_path
        file_store[summary_file_path] = summary.encode("utf-8")

        logger.info(f"Text summary saved as {summary_file_path}. Generating audio...")
        
        audio_file = io.BytesIO()
        text_to_speech(summary, audio_file)
        audio_file.seek(0)
        file_store[audio_file_path] = audio_file.read()

        logger.info(f"Audio file saved as {audio_file_path}. Summary processing complete.")

        return {
            "summary": summary,
            "summary_file": "/download-summary-text/",
            "voice_file": "/download-summary-audio/"
        }

    except Exception as e:
        logger.error(f"Error summarizing text: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to summarize text.")

@app.get("/download-summary-text/")
async def download_summary_text():
    """Endpoint to download the last generated summary text file."""
    if "last_summary_file" not in file_store:
        logger.warning("Download summary text request failed: No summary file found.")
        raise HTTPException(status_code=404, detail="No summary file found.")

    summary_file_path = file_store["last_summary_file"]

    if summary_file_path not in file_store:
        logger.warning(f"Summary file {summary_file_path} not found in storage.")
        raise HTTPException(status_code=404, detail="Summary file not found.")

    logger.info(f"Downloading summary file: {summary_file_path}")
    return StreamingResponse(io.BytesIO(file_store[summary_file_path]), 
                             media_type="text/plain", 
                             headers={"Content-Disposition": f"attachment; filename={os.path.basename(summary_file_path)}"})

@app.get("/download-summary-audio/")
async def download_summary_audio():
    """Endpoint to download the last generated summary audio file."""
    if "last_audio_file" not in file_store:
        logger.warning("Download summary audio request failed: No audio file found.")
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
