from fastapi import FastAPI, UploadFile, Form, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from summarization_functions import process_document_function
from summarization_functions import process_query_function
from summarization_functions import summarize_text_function
from summarization_functions import generate_notes_function
from summarization_functions import get_summary_file
from summarization_functions import get_audio_file
from summarization_functions import get_pdf_file
from rag import RAGModel
import yaml
import logging


# Load logging configuration
with open("logging_config.yaml", "r") as file:
    config = yaml.safe_load(file)
    logging.config.dictConfig(config)

logger = logging.getLogger("myapp")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize RAG Model
try:
    logger.info("Initializing RAG Model...")
    rag_model = RAGModel(
        model_path='DharaneSegar/flant5-bio-summarization',
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


@app.post("/process-document/")
async def process_document(request: Request, file: UploadFile, word_count: int = Form(...)):
    """
    Endpoint to process a document: extract, summarize, and convert to speech.
    """
    summary, task_id = await process_document_function(request, file, word_count, rag_model)

    if summary is None:
        raise HTTPException(status_code=499, detail="Request was canceled.")

    return {
        "status": "success",
        "message": "Document processed successfully.",
        "summary": summary,
        "summary_file": f"/download-summary-text/{task_id}",
        "voice_file": f"/download-summary-audio/{task_id}"
    }


@app.post("/process-query/")
async def process_query(request: Request, query: str = Form(...), word_count: int = Form(...)):
    """
    Endpoint to retrieve and summarize content based on a query.
    """
    summary, task_id = await process_query_function(request, query, word_count, rag_model)

    if summary is None:
        raise HTTPException(status_code=499, detail="Request was canceled.")

    return {
        "status": "success",
        "message": "Query processed successfully.",
        "summary": summary,
        "summary_file": f"/download-summary-text/{task_id}",
        "voice_file": f"/download-summary-audio/{task_id}"
    }


@app.post("/summarize-text/")
async def summarize_text(request: Request, text: str = Form(...), word_count: int = Form(...)):
    """
    Endpoint to summarize a given text.
    """
    summary, task_id = await summarize_text_function(request, text, word_count, rag_model)

    if summary is None:
        raise HTTPException(status_code=499, detail="Request was canceled.")

    return {
        "status": "success",
        "message": "Summary generated successfully.",
        "summary": summary,
        "summary_file": f"/download-summary-text/{task_id}",
        "voice_file": f"/download-summary-audio/{task_id}"
    }


@app.post("/generate-notes/")
async def generate_notes(
    request: Request,
    topic: str = Form(...),
    lang: str = Form(None)  # Optional: "ta" (Tamil) or "si" (Sinhala)
):
    """
    Endpoint to generate structured notes for a given topic.
    """
    response = await generate_notes_function(request, topic, lang, rag_model)

    if response is None:
        raise HTTPException(status_code=499, detail="Request was canceled.")

    return JSONResponse(content=response)


@app.get("/download-summary-text/{task_id}")
async def download_summary_text(task_id: str):
    """
    Endpoint to download a summary text file based on task_id.
    Works for all three APIs: process-document, process-query, and summarize-text.
    """
    return await get_summary_file(task_id)


@app.get("/download-summary-audio/{task_id}")
async def download_summary_audio(task_id: str):
    """
    Endpoint to download a summary audio file based on task_id.
    Works for all three APIs: process-document, process-query, and summarize-text.
    """
    return await get_audio_file(task_id)


@app.get("/download-notes/{file_name}")
async def download_notes(file_name: str):
    """
    Endpoint to download the generated notes PDF file.
    """
    return await get_pdf_file(file_name)


# start application
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8002)
