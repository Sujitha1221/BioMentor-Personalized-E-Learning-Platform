import io
import asyncio
import hashlib
import logging
from fastapi import Request, HTTPException, BackgroundTasks
from text_extraction_service import extract_content, clean_text, format_as_paragraph
from voice_service import text_to_speech
from file_handler import save_uploaded_file, generate_pdf
import io
import hashlib
import asyncio
import yaml
from fastapi.responses import StreamingResponse


with open("logging_config.yaml", "r") as file:
    config = yaml.safe_load(file)
    logging.config.dictConfig(config)

logger = logging.getLogger("myapp")

file_store = {}  # Temporary storage for files
ongoing_tasks = {}  # Track running tasks


async def process_document_function(request: Request, file, word_count, rag_model):
    """
    Handles document processing: extraction, summarization, and text-to-speech conversion.
    Ensures request cancellations do not keep processing.
    """
    task_id = hashlib.md5(file.filename.encode()).hexdigest()

    # Cancel existing task if already running
    if task_id in ongoing_tasks:
        logger.warning(f"Cancelling previous request for {file.filename}")
        ongoing_tasks[task_id].cancel()
        del ongoing_tasks[task_id]

    async def process():
        try:
            logger.info(f"Processing document: {file.filename}")

            # Step 1: Save uploaded file
            file_path = save_uploaded_file(file)
            logger.info(f"File saved to {file_path}. Extracting content...")

            raw_text = extract_content(file_path)

            if not raw_text.strip():
                logger.warning(f"No content extracted from {file.filename}.")
                raise HTTPException(
                    status_code=400, detail="No content extracted.")

            # Check if the client disconnected before proceeding
            if await request.is_disconnected():
                logger.warning(
                    f"Request was canceled. Stopping processing for {file.filename}.")
                return None

            # Step 2: Clean and format text
            cleaned_text = clean_text(raw_text)
            formatted_text = format_as_paragraph(cleaned_text)

            # Check again before summarization
            if await request.is_disconnected():
                logger.warning(
                    f"Request was canceled. Stopping processing for {file.filename}.")
                return None

            # Generate summary
            logger.info(f"Generating summary for {file.filename}...")

            # Step 3: Generate summary
            summary = rag_model.generate_summary_for_long_text(
                formatted_text, max_words=word_count)

            if not summary:
                logger.warning(
                    f"Failed to generate summary for {file.filename}.")
                raise HTTPException(
                    status_code=500, detail="Summary generation failed.")

            summary_file_path = f"summary_{task_id}.pdf"
            audio_file_path = f"summary_{task_id}.mp3"

            # Generate PDF
            pdf_data = generate_pdf(summary, topic="Summary")
            file_store[summary_file_path] = pdf_data

            logger.info(
                f"PDF summary saved as {summary_file_path}. Generating audio...")

            # Check before generating audio
            if await request.is_disconnected():
                logger.warning(
                    f"Request was canceled. Stopping processing for {file.filename}.")
                return None

            # Step 4: Convert summary to speech
            audio_file = io.BytesIO()
            text_to_speech(summary, audio_file)
            audio_file.seek(0)
            file_store[audio_file_path] = audio_file.read()

            logger.info(
                f"Audio file saved as {audio_file_path}. Processing complete.")

            # Cleanup task tracking
            del ongoing_tasks[task_id]

            return summary, task_id

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
    return await task


async def process_query_function(request: Request, query, word_count, rag_model):
    """
    Handles query-based retrieval and summarization logic.
    Ensures request cancellations do not keep processing.
    """
    task_id = hashlib.sha256(query.encode()).hexdigest()[:10]

    # Cancel existing task if already running
    if task_id in ongoing_tasks:
        logger.warning(f"Cancelling previous request for query: {query}")
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
                logger.warning("Generated summary is empty.")
                raise HTTPException(
                    status_code=400, detail="Generated summary is empty.")

            summary_file_path = f"summary_{task_id}.pdf"
            audio_file_path = f"summary_{task_id}.mp3"

            # Generate PDF
            pdf_data = generate_pdf(summary, topic="Summary")
            file_store[summary_file_path] = pdf_data

            logger.info(
                f"PDF summary saved as {summary_file_path}. Generating audio...")

            # Check if request is disconnected before generating audio
            if await request.is_disconnected():
                logger.warning(
                    "Request was canceled. Stopping audio generation.")
                return None, None

            # Step 4: Convert summary to audio
            audio_file = io.BytesIO()
            text_to_speech(summary, audio_file)
            audio_file.seek(0)
            file_store[audio_file_path] = audio_file.read()

            logger.info(
                f"Audio file saved as {audio_file_path}. Summary processing complete.")

            # Cleanup after task completion
            del ongoing_tasks[task_id]

            return summary, task_id

        except asyncio.CancelledError:
            logger.warning(f"Processing for query '{query}' was canceled.")
            del ongoing_tasks[task_id]
            return None, None

        except HTTPException as http_error:
            del ongoing_tasks[task_id]
            raise http_error  # Return FastAPI HTTPException directly

        except Exception as e:
            logger.error(
                f"Unexpected error processing query: {e}", exc_info=True)
            del ongoing_tasks[task_id]
            raise HTTPException(
                status_code=500, detail="Failed to process query.")

    # Store and run the task in the background
    task = asyncio.create_task(process())
    ongoing_tasks[task_id] = task

    return await task


async def summarize_text_function(request: Request, text, word_count, rag_model):
    """
    Handles summarization of provided text input and converts the summary to speech.
    Ensures request cancellations do not keep processing.
    """
    task_id = hashlib.sha256(text.encode()).hexdigest()[:10]

    # Cancel existing task if already running
    if task_id in ongoing_tasks:
        logger.warning("Cancelling previous summarization request.")
        ongoing_tasks[task_id].cancel()
        del ongoing_tasks[task_id]

    async def process():
        try:
            logger.info("Processing text summarization request.")

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

            summary_file_path = f"summary_{task_id}.pdf"
            audio_file_path = f"summary_{task_id}.mp3"

            # Generate PDF
            pdf_data = generate_pdf(summary, topic="Summary")
            file_store[summary_file_path] = pdf_data

            logger.info(
                f"PDF summary saved as {summary_file_path}. Generating audio...")

            # Check if request is disconnected before generating audio
            if await request.is_disconnected():
                logger.warning(
                    "Request was canceled. Stopping audio generation.")
                return None, None

            # Step 3: Convert summary to audio
            audio_file = io.BytesIO()
            text_to_speech(summary, audio_file)
            audio_file.seek(0)
            file_store[audio_file_path] = audio_file.read()

            logger.info(
                f"Audio file saved as {audio_file_path}. Summary processing complete.")

            # Cleanup after task completion
            del ongoing_tasks[task_id]

            return summary, task_id

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
                status_code=500, detail="Failed to summarize text.")

    # Store and run the task in the background
    task = asyncio.create_task(process())
    ongoing_tasks[task_id] = task

    return await task


async def generate_notes_function(request: Request, topic, lang, rag_model):
    """
    Handles structured notes generation, including optional translation and PDF generation.
    """
    task_id = hashlib.sha256(f"{topic}_{lang}".encode()).hexdigest()[:10]

    # Cancel existing task if already running
    if task_id in ongoing_tasks:
        logger.warning(f"Cancelling previous notes request for topic: {topic}")
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

            if await request.is_disconnected():
                return None

            # Step 6: Conditional PDF Generation (Only for English)
            if lang_name == "English":
                pdf_bytes = generate_pdf(structured_notes, topic)
                pdf_filename = f"notes_{topic.replace(' ', '_')}_{lang_name}.pdf"

                # Store in memory
                file_store[pdf_filename] = pdf_bytes
                logger.info(f"PDF Stored: {pdf_filename}")

                # Handle disconnected client
                if await request.is_disconnected():
                    return None

                # Cleanup task
                del ongoing_tasks[task_id]

                return {
                    "structured_notes": structured_notes,
                    "download_link": f"/download-notes/{pdf_filename}"
                }

            else:
                # For Tamil or Sinhala, do NOT generate/return PDF
                if await request.is_disconnected():
                    return None

                # Cleanup task
                del ongoing_tasks[task_id]

                return {"structured_notes": structured_notes}

        except asyncio.CancelledError:
            logger.warning(
                f"Generating notes for topic '{topic}' was canceled.")
            del ongoing_tasks[task_id]
            return None

        except HTTPException as http_exc:
            """ Handle expected errors like inappropriate content or missing data """
            del ongoing_tasks[task_id]
            logger.error(f"HTTPException: {http_exc.detail}")
            raise http_exc  # Preserves error messages

        except Exception as e:
            logger.error(
                f"Error generating notes for '{topic}' in '{lang}': {e}", exc_info=True)
            del ongoing_tasks[task_id]
            raise HTTPException(
                status_code=500, detail="Failed to generate notes.")

    # Store and run the task in the background
    task = asyncio.create_task(process())
    ongoing_tasks[task_id] = task
    return await task


async def get_summary_file(task_id: str):
    """
    Retrieves and streams a PDF summary file based on the provided task_id.
    """
    summary_file_path = f"summary_{task_id}.pdf"

    if summary_file_path not in file_store:
        logger.warning(f"Summary PDF file {summary_file_path} not found.")
        raise HTTPException(status_code=404, detail="Summary file not found.")

    logger.info(f"Downloading summary PDF file: {summary_file_path}")
    return StreamingResponse(io.BytesIO(file_store[summary_file_path]),
                             media_type="application/pdf",
                             headers={"Content-Disposition": f"attachment; filename={summary_file_path}"})


async def get_audio_file(task_id: str):
    """
    Retrieves and streams a summary audio file based on the provided task_id.
    """
    audio_file_path = f"summary_{task_id}.mp3"

    if audio_file_path not in file_store:
        logger.warning(f"Audio file {audio_file_path} not found.")
        raise HTTPException(status_code=404, detail="Audio file not found.")

    logger.info(f"Downloading audio file: {audio_file_path}")
    return StreamingResponse(io.BytesIO(file_store[audio_file_path]),
                             media_type="audio/mpeg",
                             headers={"Content-Disposition": f"attachment; filename={audio_file_path}"})


async def get_pdf_file(file_name: str):
    """
    Retrieves and streams a generated notes PDF file.
    """
    if file_name not in file_store:
        logger.warning(f"Notes file '{file_name}' NOT FOUND in `file_store`")
        raise HTTPException(status_code=404, detail="Notes file not found.")

    logger.info(f"Downloading notes file: {file_name}")

    return StreamingResponse(io.BytesIO(file_store[file_name]),
                             media_type="application/pdf",
                             headers={"Content-Disposition": f"attachment; filename={file_name}"})
