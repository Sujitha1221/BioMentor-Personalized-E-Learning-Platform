import logging
import logging.config
import yaml
from rag import RAGModel
from text_extraction_service import extract_content, clean_text, format_as_paragraph
from voice_service import text_to_speech
from file_handler import save_uploaded_file, generate_pdf
import io
import hashlib
import asyncio
from fastapi import Request, BackgroundTasks
from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
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

# Track running tasks
ongoing_tasks = {}


@app.post("/process-document/")
async def process_document(request: Request, background_tasks: BackgroundTasks, file: UploadFile, word_count: int = Form(...)):
    """
    Process a document to extract, summarize, and generate a voice file.
    Ensures request cancellations do not keep processing.
    Also checks for inappropriate content before processing.
    """
    task_id = hashlib.md5(file.filename.encode()).hexdigest(
    )  # Unique identifier for each request

    # If a task is already running for this file, cancel it
    if task_id in ongoing_tasks:
        logger.warning(
            f"Previous request for {file.filename} is still running. Cancelling old task.")
        ongoing_tasks[task_id].cancel()
        del ongoing_tasks[task_id]

    async def process():
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

            # Check if request is canceled before heavy processing
            if await request.is_disconnected():
                logger.warning(
                    f"Request was canceled. Stopping processing for {file.filename}.")
                return None

            # Clean and format text
            cleaned_text = clean_text(raw_text)
            formatted_text = format_as_paragraph(cleaned_text)

            # Check again before summarization
            if await request.is_disconnected():
                logger.warning(
                    f"Request was canceled. Stopping processing for {file.filename}.")
                return None

            # Generate summary
            logger.info(f"Generating summary for {file.filename}...")
            summary = rag_model.generate_summary_for_long_text(
                formatted_text, max_words=word_count)

            if not summary:
                logger.warning(
                    f"Failed to generate summary for {file.filename}.")
                raise HTTPException(
                    status_code=500, detail="Summary generation failed.")

            # Generate **unique** filenames
            summary_file_path = f"summary_{task_id}.txt"
            audio_file_path = f"summary_{task_id}.mp3"

            # Save summary in memory using task_id
            file_store[summary_file_path] = summary.encode("utf-8")

            logger.info(
                f"Summary saved as {summary_file_path}. Generating audio...")

            # Check before generating audio
            if await request.is_disconnected():
                logger.warning(
                    f"Request was canceled. Stopping processing for {file.filename}.")
                return None

            # Generate audio file
            audio_file = io.BytesIO()
            text_to_speech(summary, audio_file)
            audio_file.seek(0)
            file_store[audio_file_path] = audio_file.read()

            logger.info(
                f"Audio file saved as {audio_file_path}. Processing complete.")

            # Cleanup after task completion
            del ongoing_tasks[task_id]

            return summary, task_id  # Return the summary and unique ID

        except asyncio.CancelledError:
            logger.warning(f"Processing for {file.filename} was canceled.")
            del ongoing_tasks[task_id]
            return None, None

        except HTTPException as http_err:
            del ongoing_tasks[task_id]
            raise http_err  # Return FastAPI HTTPException directly

        except Exception as e:
            logger.error(
                f"Error processing document {file.filename}: {e}", exc_info=True)
            del ongoing_tasks[task_id]
            raise HTTPException(
                status_code=500, detail="Failed to process document.")

    # Store and run the task in the background
    task = asyncio.create_task(process())
    ongoing_tasks[task_id] = task
    background_tasks.add_task(task)

    # **Wait for the task to complete before returning the response**
    summary, task_id = await task

    if summary is None:
        # 499 Client Closed Request
        raise HTTPException(status_code=499, detail="Request was canceled.")

    return {
        "status": "success",
        "message": "Document processed successfully.",
        "summary": summary,  # Returns the actual summary
        "summary_file": f"/download-summary-text/{task_id}",
        "voice_file": f"/download-summary-audio/{task_id}"
    }


@app.post("/process-query/")
async def process_query(request: Request, background_tasks: BackgroundTasks, query: str = Form(...), word_count: int = Form(...)):
    """
    Retrieve and summarize content based on a query and return results as an API response.
    Ensures request cancellations do not keep processing.
    Uses the same /download-summary-text/ and /download-summary-audio/ endpoints for downloading results.
    """
    task_id = hashlib.sha256(query.encode()).hexdigest()[
        :10]  # Unique identifier for each query

    # If a task is already running for this query, cancel it
    if task_id in ongoing_tasks:
        logger.warning(
            f"Previous request for query '{query}' is still running. Cancelling old task.")
        ongoing_tasks[task_id].cancel()
        del ongoing_tasks[task_id]

    async def process():
        try:
            logger.info(f"Processing query: {query}")

            # Step 1: Check for inappropriate content
            inappropriate_message = rag_model.contains_inappropriate_content(
                query)
            if inappropriate_message:
                logger.warning(f"Inappropriate content detected: {query}")
                raise HTTPException(
                    status_code=400, detail=inappropriate_message)

            # Check if request is disconnected before retrieving content
            if await request.is_disconnected():
                logger.warning(
                    f"Request was canceled. Stopping processing for query: {query}")
                return None, None  # Return None to indicate cancellation

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

            # Check if request is disconnected before summarization
            if await request.is_disconnected():
                logger.warning(
                    f"Request was canceled. Stopping processing for query: {query}")
                return None, None

            # Step 3: Generate Summary
            combined_text = " ".join(relevant_texts)
            summary = rag_model.generate_summary_for_long_text(
                combined_text, max_words=word_count)

            if not summary.strip():
                logger.warning(
                    f"Generated summary is empty for query: {query}")
                raise HTTPException(
                    status_code=500, detail="Failed to generate a summary.")

            # Step 4: Generate stable filenames using task_id
            summary_file_path = f"summary_{task_id}.txt"
            audio_file_path = f"summary_{task_id}.mp3"

            # Store summary text file using task_id
            file_store[summary_file_path] = summary.encode("utf-8")
            logger.info(f"Query summary saved as {summary_file_path}.")

            # Check if request is disconnected before generating audio
            if await request.is_disconnected():
                logger.warning(
                    f"Request was canceled. Stopping processing for query: {query}")
                return None, None

            # Step 5: Convert summary to audio
            audio_file = io.BytesIO()
            text_to_speech(summary, audio_file)
            audio_file.seek(0)
            file_store[audio_file_path] = audio_file.read()
            logger.info(f"Query audio saved as {audio_file_path}.")

            # Cleanup after task completion
            del ongoing_tasks[task_id]

            return summary, task_id  # Return summary and unique task_id

        except asyncio.CancelledError:
            logger.warning(f"Processing for query '{query}' was canceled.")
            del ongoing_tasks[task_id]
            return None, None

        except HTTPException as http_err:
            del ongoing_tasks[task_id]
            raise http_err  # Return FastAPI HTTPException directly

        except Exception as e:
            logger.error(
                f"Unexpected error processing query: {e}", exc_info=True)
            del ongoing_tasks[task_id]
            raise HTTPException(
                status_code=500, detail="An unexpected error occurred while processing the query.")

    # Store and run the task in the background
    task = asyncio.create_task(process())
    ongoing_tasks[task_id] = task
    background_tasks.add_task(task)

    # **Wait for the task to complete before returning the response**
    summary, task_id = await task

    if summary is None:
        # 499 Client Closed Request
        raise HTTPException(status_code=499, detail="Request was canceled.")

    return {
        "status": "success",
        "message": "Query processed successfully.",
        "summary": summary,  # Now returns the actual summary
        "summary_file": f"/download-summary-text/{task_id}",
        "voice_file": f"/download-summary-audio/{task_id}"
    }


@app.post("/summarize-text/")
async def summarize_text(request: Request, background_tasks: BackgroundTasks, text: str = Form(...), word_count: int = Form(...)):
    """
    Summarizes a long text input and provides separate endpoints to download files.
    Ensures request cancellations are handled properly.
    Uses the same /download-summary-text/ and /download-summary-audio/ endpoints for downloading results.
    """
    task_id = hashlib.sha256(text.encode()).hexdigest()[
        :10]  # Unique identifier for each request

    # If a task is already running for this text, cancel it
    if task_id in ongoing_tasks:
        logger.warning(
            "Previous summarization request is still running. Cancelling old task.")
        ongoing_tasks[task_id].cancel()
        del ongoing_tasks[task_id]

    async def process():
        try:
            logger.info("Received request to summarize text.")

            if not text.strip():
                logger.warning("Empty text input received.")
                raise HTTPException(
                    status_code=400, detail="Text input cannot be empty.")

            # Step 1: Check for inappropriate content
            inappropriate_response = rag_model.contains_inappropriate_content(
                text)
            if inappropriate_response:
                logger.warning("Inappropriate content detected in text input.")
                raise HTTPException(
                    status_code=400, detail=inappropriate_response)

            # Check if request is disconnected before processing
            if await request.is_disconnected():
                logger.warning("Request was canceled. Stopping summarization.")
                return None, None

            # Step 2: Generate summary
            summary = rag_model.generate_summary_for_long_text(
                text, max_words=word_count)

            if not summary.strip():
                logger.warning("Generated summary is empty.")
                raise HTTPException(
                    status_code=400, detail="Generated summary is empty.")

            # Step 3: Generate file paths using task_id
            summary_file_path = f"summary_{task_id}.txt"
            audio_file_path = f"summary_{task_id}.mp3"

            # Store summary text file using task_id
            file_store[summary_file_path] = summary.encode("utf-8")

            logger.info(
                f"Text summary saved as {summary_file_path}. Generating audio...")

            # Check if request is disconnected before generating audio
            if await request.is_disconnected():
                logger.warning(
                    "Request was canceled. Stopping audio generation.")
                return None, None

            # Step 4: Convert text to speech
            audio_file = io.BytesIO()
            text_to_speech(summary, audio_file)
            audio_file.seek(0)
            file_store[audio_file_path] = audio_file.read()

            logger.info(
                f"Audio file saved as {audio_file_path}. Summary processing complete.")

            # Cleanup after task completion
            del ongoing_tasks[task_id]

            return summary, task_id  # Return the generated summary and unique task_id

        except asyncio.CancelledError:
            logger.warning("Summarization request was canceled.")
            del ongoing_tasks[task_id]
            return None, None

        except HTTPException as http_error:
            del ongoing_tasks[task_id]
            raise http_error  # Return FastAPI HTTPException directly

        except Exception as e:
            logger.error(f"Error summarizing text: {e}", exc_info=True)
            del ongoing_tasks[task_id]
            raise HTTPException(
                status_code=500, detail="Internal server error. Failed to summarize text.")

    # Store and run the task in the background
    task = asyncio.create_task(process())
    ongoing_tasks[task_id] = task
    background_tasks.add_task(task)

    # **Wait for the task to complete before returning the response**
    summary, task_id = await task

    if summary is None:
        # 499 Client Closed Request
        raise HTTPException(status_code=499, detail="Request was canceled.")

    return {
        "status": "success",
        "message": "Summary generated successfully.",
        "summary": summary,  # Now returns the actual summary
        "summary_file": f"/download-summary-text/{task_id}",
        "voice_file": f"/download-summary-audio/{task_id}"
    }


@app.post("/generate-notes/")
async def generate_notes(
    request: Request,
    background_tasks: BackgroundTasks,
    topic: str = Form(...),
    lang: str = Form(None)  # Optional: "ta" (Tamil) or "si" (Sinhala)
):
    """
    Generate structured notes for a given topic.
    - If a language is provided ('ta' for Tamil, 'si' for Sinhala), the notes are translated.
    - For English, a PDF file is generated and a download link is returned.
    """

    # Unique identifier for this task
    task_id = hashlib.sha256(f"{topic}_{lang}".encode()).hexdigest()[:10]

    # If a previous task exists for this topic, cancel it
    if task_id in ongoing_tasks:
        logger.warning(
            f"Previous request for '{topic}' in '{lang}' is still running. Cancelling old task.")
        ongoing_tasks[task_id].cancel()
        del ongoing_tasks[task_id]

    async def process():
        try:
            logger.info(f"Generating structured notes for topic: {topic}")

            # Step 1: Check for inappropriate content
            inappropriate_message = rag_model.contains_inappropriate_content(
                topic)
            if inappropriate_message:
                logger.warning(f"Inappropriate topic detected: {topic}")
                raise HTTPException(
                    status_code=400, detail=inappropriate_message)

            # Step 2: Retrieve relevant content
            relevant_texts = rag_model.retrieve_relevant_content(topic)
            if not relevant_texts or relevant_texts == "No relevant content found":
                raise HTTPException(
                    status_code=404, detail="No relevant content found.")

            # Step 3: Clean and format the text
            combined_text = " ".join(relevant_texts)
            cleaned_text = rag_model._correct_and_format_text(combined_text)

            # Step 4: Generate structured notes
            structured_notes = rag_model.generate_structured_notes(
                cleaned_text, topic)

            # Step 5: Translate if necessary
            if lang in ["ta", "si"]:
                structured_notes = await rag_model.translate_text(structured_notes, lang)
                lang_name = "Tamil" if lang == "ta" else "Sinhala"
            else:
                lang_name = "English"

            logger.info(
                f"Structured notes generated (first 100 chars): {structured_notes[:100]}...")

            # Step 6: Conditional PDF Generation (Only for English)
            if lang_name == "English":
                pdf_bytes = generate_pdf(structured_notes, topic)
                pdf_filename = f"notes_{topic.replace(' ', '_')}_{lang_name}.pdf"

                # Store in memory
                file_store[pdf_filename] = pdf_bytes
                logging.info(f"PDF Stored: {pdf_filename}")

                # Step 7: Handle disconnected client
                if await request.is_disconnected():
                    return None

                # Cleanup task
                del ongoing_tasks[task_id]

                # Return structured notes and PDF download link
                return JSONResponse(content={
                    "structured_notes": structured_notes,
                    "download_link": f"/download-notes/{pdf_filename}"
                })

            else:
                # For Tamil or Sinhala, do NOT generate/return PDF
                if await request.is_disconnected():
                    return None

                # Cleanup task
                del ongoing_tasks[task_id]

                # Return only structured notes
                return JSONResponse(content={"structured_notes": structured_notes})

        except HTTPException as http_exc:
            """ Handle expected errors like inappropriate content or missing data """
            del ongoing_tasks[task_id]
            logger.error(f"HTTPException: {http_exc.detail}")
            raise http_exc  # Preserves error messages

        except Exception as e:
            """ Handle unexpected errors and return a detailed message """
            logging.error(
                f"Unexpected error generating notes for '{topic}' in '{lang}': {e}", exc_info=True)
            del ongoing_tasks[task_id]
            # Returns actual error message
            raise HTTPException(status_code=500, detail=str(e))

    # Run the process in the background
    task = asyncio.create_task(process())
    ongoing_tasks[task_id] = task
    background_tasks.add_task(task)

    response = await task
    if response is None:
        raise HTTPException(status_code=499, detail="Request was canceled.")

    return response


@app.get("/download-summary-text/{task_id}")
async def download_summary_text(task_id: str):
    """
    Endpoint to download a summary text file based on task_id.
    This works for all three APIs: process-document, process-query, and summarize-text.
    """
    summary_file_path = f"summary_{task_id}.txt"

    if summary_file_path not in file_store:
        logger.warning(f"Summary file {summary_file_path} not found.")
        raise HTTPException(status_code=404, detail="Summary file not found.")

    logger.info(f"Downloading summary file: {summary_file_path}")
    return StreamingResponse(io.BytesIO(file_store[summary_file_path]),
                             media_type="text/plain",
                             headers={"Content-Disposition": f"attachment; filename={summary_file_path}"})


@app.get("/download-summary-audio/{task_id}")
async def download_summary_audio(task_id: str):
    """
    Endpoint to download a summary audio file based on task_id.
    This works for all three APIs: process-document, process-query, and summarize-text.
    """
    audio_file_path = f"summary_{task_id}.mp3"

    if audio_file_path not in file_store:
        logger.warning(f"Audio file {audio_file_path} not found.")
        raise HTTPException(status_code=404, detail="Audio file not found.")

    logger.info(f"Downloading audio file: {audio_file_path}")
    return StreamingResponse(io.BytesIO(file_store[audio_file_path]),
                             media_type="audio/mpeg",
                             headers={"Content-Disposition": f"attachment; filename={audio_file_path}"})


@app.get("/download-notes/{file_name}")
async def download_notes(file_name: str):
    """
    Endpoint to download the generated notes PDF file.
    """
    if file_name not in file_store:
        logging.warning(f"Notes file '{file_name}' NOT FOUND in `file_store`")
        raise HTTPException(status_code=404, detail="Notes file not found.")

    logging.info(f"Downloading notes file: {file_name}")

    # Retrieve the PDF bytes and serve it
    return StreamingResponse(io.BytesIO(file_store[file_name]),
                             media_type="application/pdf",
                             headers={"Content-Disposition": f"attachment; filename={file_name}"})


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8002)
