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
    rag_model = RAGModel(
        model_path='D:/Downloads/RP/Summarization/flan_t5_finetuned_model',
        embedding_model_name='all-MiniLM-L6-v2',
        dataset_paths=[
            '../../Model-Training/bio_summary_keywords.csv',
            '../../Model-Training/biology_information_retrieval_sample.csv'
        ]
    )
    logger.info("RAG Model initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize RAG Model: {e}")
    raise

file_store = {}  # Temporary storage for files

@app.post("/process-document/")
async def process_document(file: UploadFile, word_count: int = Form(...)):
    """
    Process a document to extract, summarize, and generate a voice file,
    then return the output files as API responses.
    """
    try:
        logger.info("Processing document upload.")
        file_path = save_uploaded_file(file)
        raw_text = extract_content(file_path)

        if not raw_text.strip():
            logger.warning("No content could be extracted from the document.")
            raise HTTPException(status_code=400, detail="No content could be extracted from the document.")

        cleaned_text = clean_text(raw_text)
        formatted_text = format_as_paragraph(cleaned_text)

        # Generate a summary
        summary = rag_model.generate_summary_for_long_text(formatted_text, max_words=word_count)

        # Save summary in memory
        summary_bytes = summary.encode("utf-8")
        file_store["summary.txt"] = summary_bytes
        
        # Generate voice file
        audio_file = io.BytesIO()
        text_to_speech(summary, audio_file)
        audio_file.seek(0)
        file_store["summary.mp3"] = audio_file.read()

        logger.info("Document processed successfully.")

        return {
            "summary": summary,
            "summary_file": "/download-summary-text/",
            "voice_file": "/download-summary-audio/"
        }
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail="Failed to process document.")

@app.post("/process-query/")
async def process_query(query: str = Form(...), word_count: int = Form(...)):
    """
    Retrieve and summarize content based on a query and return results as an API response.
    """
    try:
        logger.info(f"Processing query: {query}")
        
        # Retrieve relevant texts
        relevant_texts = rag_model.retrieve_relevant_content(query)
        if not relevant_texts:
            logger.warning("No relevant content found for the query.")
            raise HTTPException(status_code=400, detail="No relevant content found for the given query.")
        
        combined_text = " ".join(relevant_texts)
        summary = rag_model.generate_summary_for_long_text(combined_text, max_words=word_count)
        
        # Save summary in memory
        summary_bytes = summary.encode("utf-8")
        file_store["summary.txt"] = summary_bytes
        
        # Generate voice file
        audio_file = io.BytesIO()
        text_to_speech(summary, audio_file)
        audio_file.seek(0)
        file_store["summary.mp3"] = audio_file.read()

        logger.info("Query processed successfully.")

        return {
            "summary": summary,
            "summary_file": "/download-summary-text/",
            "voice_file": "/download-summary-audio/"
        }
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail="Failed to process query.")


@app.post("/summarize-text/")
async def summarize_text(text: str = Form(...), word_count: int = Form(...)):
    """
    Summarizes a long text input and provides separate endpoints to download files.
    """
    try:
        logger.info("Received request to summarize text.")
        if not text.strip():
            raise HTTPException(status_code=400, detail="Text input cannot be empty.")

        summary = rag_model.generate_summary_for_long_text(text, max_words=word_count)

        # Save summary in memory
        summary_bytes = summary.encode("utf-8")
        file_store["summary.txt"] = summary_bytes
        
        # Generate voice file
        audio_file = io.BytesIO()
        text_to_speech(summary, audio_file)
        audio_file.seek(0)
        file_store["summary.mp3"] = audio_file.read()

        return {
            "summary": summary,
            "summary_file": "/download-summary-text/",
            "voice_file": "/download-summary-audio/"
        }

    except Exception as e:
        logger.error(f"Error summarizing text: {e}")
        raise HTTPException(status_code=500, detail="Failed to summarize text.")

@app.get("/download-summary-text/")
async def download_summary_text():
    """Endpoint to download the summary text file."""
    if "summary.txt" not in file_store:
        raise HTTPException(status_code=404, detail="Summary file not found.")
    return StreamingResponse(io.BytesIO(file_store["summary.txt"]), media_type="text/plain", headers={"Content-Disposition": "attachment; filename=summary.txt"})

@app.get("/download-summary-audio/")
async def download_summary_audio():
    """Endpoint to download the summary audio file."""
    if "summary.mp3" not in file_store:
        raise HTTPException(status_code=404, detail="Audio file not found.")
    return StreamingResponse(io.BytesIO(file_store["summary.mp3"]), media_type="audio/mpeg", headers={"Content-Disposition": "attachment; filename=summary.mp3"})



if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
