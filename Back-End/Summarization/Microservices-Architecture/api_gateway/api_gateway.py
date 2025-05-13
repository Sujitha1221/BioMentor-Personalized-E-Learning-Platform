import asyncio
import hashlib
import io
import logging
import logging.config
import requests
import yaml
from fastapi import FastAPI, UploadFile, Form, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

app = FastAPI()

# Load logging configuration
with open("logging_config.yaml", "r") as file:
    config = yaml.safe_load(file)
    logging.config.dictConfig(config)

logger = logging.getLogger("api_gateway")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Microservices URLs
TEXT_EXTRACTION_SERVICE = "http://text_extraction_service:8001"
SUMMARIZATION_SERVICE = "http://summarization_service:8002"
VOICE_SERVICE = "http://voice_service:8003"
FILE_SERVICE = "http://file_service:8004"

file_store = {}  # Temporary storage for files

# Keep track of ongoing tasks so we can cancel old ones
ongoing_tasks = {}


@app.post("/process-document/")
async def process_document(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile,
    word_count: int = Form(...),
):
    """
    Process a document to extract text, summarize it, and generate a voice file.
    - Uses a unique task_id for each request.
    - Cancels any ongoing task for the same file.
    - Checks for request cancellation at multiple steps.
    """
    # 1) Generate a unique ID for this file request
    task_id = hashlib.md5(file.filename.encode()).hexdigest()

    # 2) Cancel any previously ongoing task for this file
    if task_id in ongoing_tasks:
        logger.warning(
            f"Previous request for '{file.filename}' is still running. Cancelling old task."
        )
        ongoing_tasks[task_id].cancel()
        del ongoing_tasks[task_id]

    async def process():
        try:
            # ------------------------------------------
            # 1) Upload file to FILE_SERVICE
            # ------------------------------------------
            logger.info(f"Uploading file '{file.filename}' to FILE_SERVICE...")
            try:
                file_bytes = file.file.read()
                file.file.seek(0)
                upload_resp = requests.post(
                    f"{FILE_SERVICE}/upload/",
                    files={"file": (file.filename, file_bytes)},

                )
                if upload_resp.status_code != 200:
                    logger.error("File upload to FILE_SERVICE failed.")
                    raise HTTPException(
                        status_code=500, detail="File upload failed."
                    )
                file_path = upload_resp.json().get("file_path", "")
                logger.info(f"File uploaded successfully: {file_path}")
            except Exception as e:
                logger.error(f"Error uploading file: {e}", exc_info=True)
                raise HTTPException(
                    status_code=500, detail="File upload failed.")

            if await request.is_disconnected():
                logger.warning("Request was canceled by the client.")
                return None

            # ------------------------------------------
            # 2) Extract text from the uploaded file
            # ------------------------------------------
            logger.info("Extracting text from the uploaded file...")
            try:
                extract_resp = requests.post(
                    f"{TEXT_EXTRACTION_SERVICE}/extract/",
                    json={"file_path": file_path},
                )
                if extract_resp.status_code != 200:
                    raise HTTPException(
                        status_code=500, detail="Text extraction failed."
                    )
                extracted_text = extract_resp.json().get("text", "").strip()
                if not extracted_text:
                    raise HTTPException(
                        status_code=400,
                        detail="No text could be extracted from the document.",
                    )
                logger.info("Text extracted successfully.")
            except Exception as e:
                logger.error(f"Error extracting text: {e}", exc_info=True)
                raise HTTPException(
                    status_code=500, detail="Text extraction failed.")

            if await request.is_disconnected():
                logger.warning("Request was canceled by the client.")
                return None

            # ------------------------------------------
            # 3) Summarize text using the Summarization Service
            # ------------------------------------------
            logger.info("Summarizing extracted text...")
            try:
                summarize_resp = requests.post(
                    f"{SUMMARIZATION_SERVICE}/summarize/",
                    json={"text": extracted_text, "word_count": word_count},

                )
                if summarize_resp.status_code != 200:
                    raise HTTPException(
                        status_code=500, detail="Summarization failed."
                    )
                summary = summarize_resp.json().get("summary", "")
                if not summary:
                    raise HTTPException(
                        status_code=500, detail="Summary generation failed."
                    )
                logger.info("Text summarized successfully.")
            except Exception as e:
                logger.error(f"Error summarizing text: {e}", exc_info=True)
                raise HTTPException(
                    status_code=500, detail="Summarization failed.")

            if await request.is_disconnected():
                logger.warning("Request was canceled by the client.")
                return None

            # ------------------------------------------
            # 4) Generate audio using the Voice Service
            # ------------------------------------------
            logger.info("Generating audio from summary...")
            try:
                audio_resp = requests.post(
                    f"{VOICE_SERVICE}/synthesize/",
                    json={"text": summary, "file_path": f"audio_{task_id}.mp3"},
                )
                if audio_resp.status_code != 200:
                    raise HTTPException(
                        status_code=500, detail="Audio generation failed."
                    )
                logger.info("Audio generated successfully.")
            except Exception as e:
                logger.error(f"Error generating audio: {e}", exc_info=True)
                raise HTTPException(
                    status_code=500, detail="Audio generation failed.")

            return summary, task_id

        except asyncio.CancelledError:
            logger.warning(f"Processing for '{file.filename}' was canceled.")
            return None
        except HTTPException as http_err:
            raise http_err
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, detail="Failed to process document.")
        finally:
            if task_id in ongoing_tasks:
                del ongoing_tasks[task_id]

    task = asyncio.create_task(process())
    ongoing_tasks[task_id] = task
    background_tasks.add_task(task)
    result = await task
    if not result:
        raise HTTPException(status_code=499, detail="Request was canceled.")
    summary, task_id = result
    return {
        "status": "success",
        "message": "Document processed successfully.",
        "summary": summary,
        "summary_file": f"/download-summary-text/{task_id}",
        "voice_file": f"/download-summary-audio/{task_id}",
    }


@app.post("/process-query/")
async def process_query(
    request: Request,
    background_tasks: BackgroundTasks,
    query: str = Form(...),
    word_count: int = Form(...),
):
    """
    Retrieve and summarize content based on a query. Return summary and audio references.
    - Cancels any previous ongoing task for the same query.
    - Checks for client disconnection at multiple steps.
    - Uses the Summarization Service for both retrieval and summarization.
    """
    # Generate a unique ID for this query
    task_id = hashlib.sha256(query.encode()).hexdigest()[:10]

    if task_id in ongoing_tasks:
        logger.warning(
            f"Previous request for query '{query}' is still running. Cancelling old task."
        )
        ongoing_tasks[task_id].cancel()
        del ongoing_tasks[task_id]

    async def process():
        try:
            logger.info(f"Processing query: {query}")

            if await request.is_disconnected():
                logger.warning(
                    f"Request canceled by the client for query: {query}")
                return None, None

            # Retrieve relevant content using the Summarization Service's /retrieve endpoint.
            try:
                logger.info(f"Retrieving relevant content for query: {query}")
                retrieve_resp = requests.post(
                    f"{SUMMARIZATION_SERVICE}/retrieve/",
                    json={"query": query},
                )
                if retrieve_resp.status_code != 200:
                    raise HTTPException(
                        status_code=500, detail="Error retrieving relevant content."
                    )
                relevant_texts = retrieve_resp.json().get("texts", [])
                if not relevant_texts:
                    raise HTTPException(
                        status_code=404, detail="No relevant content found for the given query."
                    )
            except Exception as e:
                logger.error(f"Error retrieving content: {e}", exc_info=True)
                raise HTTPException(
                    status_code=500, detail="Error retrieving relevant content."
                )

            if await request.is_disconnected():
                logger.warning(
                    f"Request canceled by the client for query: {query}")
                return None, None

            # Summarize the retrieved content using the Summarization Service.
            combined_text = " ".join(relevant_texts)
            try:
                logger.info("Summarizing retrieved text...")
                summarize_resp = requests.post(
                    f"{SUMMARIZATION_SERVICE}/summarize/",
                    json={"text": combined_text, "word_count": word_count},

                )
                if summarize_resp.status_code != 200:
                    raise HTTPException(
                        status_code=500, detail="Summarization failed.")
                summary = summarize_resp.json().get("summary", "").strip()
                if not summary:
                    raise HTTPException(
                        status_code=500, detail="Failed to generate a summary."
                    )
                logger.info("Summarization complete.")
            except Exception as e:
                logger.error(f"Error summarizing text: {e}", exc_info=True)
                raise HTTPException(
                    status_code=500, detail="Summarization failed.")

            if await request.is_disconnected():
                logger.warning(
                    f"Request canceled by the client for query: {query}")
                return None, None

            # Generate audio from the summary using the Voice Service.
            try:
                logger.info("Generating audio from summary text...")
                audio_resp = requests.post(
                    f"{VOICE_SERVICE}/synthesize/",
                    json={"text": summary, "file_path": f"audio_{task_id}.mp3"},
                )

                if audio_resp.status_code != 200:
                    raise HTTPException(
                        status_code=500, detail="Audio generation failed."
                    )
                # The returned audio_file_path is not used further in the gateway,
                # since the File Service will later be used to download the generated file.
                _ = audio_resp.json().get("audio_file_path", "")
                logger.info("Audio generated successfully.")
            except Exception as e:
                logger.error(f"Error generating audio: {e}", exc_info=True)
                raise HTTPException(
                    status_code=500, detail="Audio generation failed.")

            if task_id in ongoing_tasks:
                del ongoing_tasks[task_id]
            return summary, task_id

        except asyncio.CancelledError:
            logger.warning(f"Processing for query '{query}' was canceled.")
            if task_id in ongoing_tasks:
                del ongoing_tasks[task_id]
            return None, None
        except HTTPException as http_err:
            if task_id in ongoing_tasks:
                del ongoing_tasks[task_id]
            raise http_err
        except Exception as e:
            logger.error(
                f"Unexpected error processing query: {e}", exc_info=True)
            if task_id in ongoing_tasks:
                del ongoing_tasks[task_id]
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred while processing the query.",
            )

    task = asyncio.create_task(process())
    ongoing_tasks[task_id] = task
    background_tasks.add_task(task)
    summary, t_id = await task
    if summary is None:
        raise HTTPException(status_code=499, detail="Request was canceled.")
    return {
        "status": "success",
        "message": "Query processed successfully.",
        "summary": summary,
        "summary_file": f"/download-summary-text/{t_id}",
        "voice_file": f"/download-summary-audio/{t_id}",
    }


@app.post("/summarize-text/")
async def summarize_text(
    request: Request,
    background_tasks: BackgroundTasks,
    text: str = Form(...),
    word_count: int = Form(...),
):
    """
    Summarizes a long text input and provides separate endpoints to download
    the generated summary and audio. Uses the Summarization Service for summarization.
    """
    task_id = hashlib.sha256(text.encode()).hexdigest()[:10]

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

            if await request.is_disconnected():
                logger.warning("Request was canceled. Stopping summarization.")
                return None, None

            # Generate summary using the Summarization Service.
            try:
                logger.info("Generating summary via Summarization Service...")
                summary_resp = requests.post(
                    f"{SUMMARIZATION_SERVICE}/summarize/",
                    json={"text": text, "word_count": word_count},
                )
                if summary_resp.status_code != 200:
                    raise HTTPException(
                        status_code=500, detail="Summarization failed.")
                summary = summary_resp.json().get("summary", "").strip()
                if not summary:
                    raise HTTPException(
                        status_code=500, detail="Generated summary is empty.")
                logger.info("Summary generation complete.")
            except Exception as e:
                logger.error("Error during summarization.", exc_info=True)
                raise HTTPException(
                    status_code=500, detail="Summarization failed.")

            if await request.is_disconnected():
                logger.warning(
                    "Request was canceled. Stopping audio generation.")
                return None, None

            # Generate audio using the Voice Service.
            try:
                logger.info("Generating audio from summary...")
                audio_resp = requests.post(
                    f"{VOICE_SERVICE}/synthesize/",
                    json={"text": summary, "file_path": f"audio_{task_id}.mp3"},
                )

                if audio_resp.status_code != 200:
                    raise HTTPException(
                        status_code=500, detail="Audio generation failed.")
                _ = audio_resp.json().get("audio_file_path", "")
                logger.info("Audio generation complete.")
            except Exception as e:
                logger.error("Error during audio generation.", exc_info=True)
                raise HTTPException(
                    status_code=500, detail="Audio generation failed.")

            summary_file_path = f"summary_{task_id}.txt"
            audio_file_key = f"summary_{task_id}.mp3"
            file_store[summary_file_path] = summary.encode("utf-8")
            file_store[audio_file_key] = b"Audio file bytes placeholder"

            if task_id in ongoing_tasks:
                del ongoing_tasks[task_id]
            return summary, task_id

        except asyncio.CancelledError:
            logger.warning("Summarization task was canceled.")
            if task_id in ongoing_tasks:
                del ongoing_tasks[task_id]
            return None, None
        except HTTPException as http_error:
            if task_id in ongoing_tasks:
                del ongoing_tasks[task_id]
            raise http_error
        except Exception as e:
            logger.error(
                "Unexpected error during summarization.", exc_info=True)
            if task_id in ongoing_tasks:
                del ongoing_tasks[task_id]
            raise HTTPException(
                status_code=500, detail="Internal server error. Failed to summarize text.")

    task = asyncio.create_task(process())
    ongoing_tasks[task_id] = task
    background_tasks.add_task(task)
    summary, t_id = await task
    if summary is None:
        raise HTTPException(status_code=499, detail="Request was canceled.")
    return {
        "status": "success",
        "message": "Summary generated successfully.",
        "summary": summary,
        "summary_file": f"/download-summary-text/{t_id}",
        "voice_file": f"/download-summary-audio/{t_id}",
    }


@app.get("/download-summary-audio/{task_id}")
async def download_summary_audio(task_id: str):
    """
    Endpoint to download a summary audio file based on task_id.
    Retrieves the file from the FILE_SERVICE.
    """
    audio_filename = f"summary_{task_id}.mp3"
    logger.info(
        f"Requesting summary audio from FILE_SERVICE: {audio_filename}")
    try:
        response = requests.get(
            f"{FILE_SERVICE}/download",
            params={"filename": audio_filename},
            stream=True,
        )
    except requests.RequestException as e:
        logger.error(f"Error contacting FILE_SERVICE: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to contact File Service.")

    if response.status_code == 404:
        logger.warning(
            f"Audio file {audio_filename} not found in File Service.")
        raise HTTPException(status_code=404, detail="Audio file not found.")
    elif response.status_code != 200:
        logger.error(
            f"File Service returned error code {response.status_code}")
        raise HTTPException(
            status_code=500, detail="Error retrieving file from File Service."
        )

    logger.info(f"Successfully retrieved audio file: {audio_filename}")
    return StreamingResponse(
        response.raw,
        media_type="audio/mpeg",
        headers={"Content-Disposition": f'attachment; filename="{audio_filename}"'},
    )


@app.get("/download-summary-text/{task_id}")
async def download_summary_text(task_id: str):
    """
    Endpoint to download a summary text file based on task_id.
    Retrieves the file from the FILE_SERVICE.
    """
    summary_filename = f"summary_{task_id}.txt"
    logger.info(
        f"Requesting summary text from FILE_SERVICE: {summary_filename}")
    try:
        response = requests.get(
            f"{FILE_SERVICE}/download",
            params={"filename": summary_filename},
            stream=True,
        )
    except requests.RequestException as e:
        logger.error(f"Error contacting FILE_SERVICE: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to contact File Service.")

    if response.status_code == 404:
        logger.warning(
            f"Summary file {summary_filename} not found in File Service.")
        raise HTTPException(status_code=404, detail="Summary file not found.")
    elif response.status_code != 200:
        logger.error(
            f"File Service returned error code {response.status_code}")
        raise HTTPException(
            status_code=500, detail="Error retrieving file from File Service."
        )

    logger.info(f"Successfully retrieved summary file: {summary_filename}")
    return StreamingResponse(
        response.raw,
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="{summary_filename}"'},
    )

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting API Gateway...")
    uvicorn.run(app, host="0.0.0.0", port=8080)
