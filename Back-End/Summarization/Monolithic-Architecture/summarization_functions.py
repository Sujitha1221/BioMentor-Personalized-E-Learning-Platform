from sklearn.feature_extraction.text import TfidfVectorizer
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
import nltk
from nltk import pos_tag
import requests
import os
import re
from dotenv import load_dotenv
from googleapiclient.discovery import build
load_dotenv()
import logging.config
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

nltk.download("averaged_perceptron_tagger_eng")
nltk.download("universal_tagset")


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

                try:
                    import io
                    audio_buffer = io.BytesIO()
                    text_to_speech(structured_notes, audio_buffer)
                    audio_filename = f"notes_{topic.replace(' ', '_')}_{lang}.mp3"
                    file_store[audio_filename] = audio_buffer.getvalue()
                    logger.info(f"Audio file stored: {audio_filename}")
                except Exception as e:
                    logger.warning(f"Voice generation failed: {e}")

                # Handle disconnected client
                if await request.is_disconnected():
                    return None

                # Cleanup task
                del ongoing_tasks[task_id]

                return {
                    "structured_notes": structured_notes,
                    "download_link": f"/download-notes/{pdf_filename}",
                    "voice_file": f"/download-notes/{audio_filename}"
                }

            else:
                # For Tamil or Sinhala, save as .txt file
                lang_display = "Tamil" if lang == "ta" else "Sinhala"
                full_text = f"{topic} - {lang_display} \n\n{structured_notes}"

                txt_bytes = full_text.encode("utf-8")
                txt_filename = f"notes_{topic.replace(' ', '_')}_{lang}.txt"

                file_store[txt_filename] = txt_bytes
                logger.info(f"Text file stored in memory: {txt_filename}")

                # Handle disconnected client
                if await request.is_disconnected():
                    return None

                # Cleanup task
                del ongoing_tasks[task_id]

                return {
                    "structured_notes": structured_notes,
                    "download_link": f"/download-notes/{txt_filename}"
                }

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

# Extract noun keywords


def is_scientific_term(term: str) -> bool:
    """
    Check if the term is relevant to scientific/biomedical domains using Wikipedia categories.
    """
    try:
        response = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "prop": "categories",
                "format": "json",
                "titles": term,
                "cllimit": "max"
            }
        )
        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            for cat in page.get("categories", []):
                cat_title = cat.get("title", "").lower()
                if any(kw in cat_title for kw in ["biology", "anatomy", "science", "medical"]):
                    return True
    except Exception as e:
        print(f"Error checking scientific term for {term}: {e}")
    return False


def extract_keywords_with_definitions(text: str):
    """
    Extract keywords (nouns) from text and return Wikipedia definitions
    for those that are scientifically relevant.
    """
    words = text.split()
    tagged = pos_tag(words, tagset="universal")

    candidate_nouns = sorted(set([
        word.strip(".,():;-").capitalize()
        for word, tag in tagged
        if tag == "NOUN" and len(word) > 4
    ]))

    results = []
    for word in candidate_nouns:
        try:
            if not is_scientific_term(word):
                continue

            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{word}"
            response = requests.get(url)
            data = response.json()

            if response.status_code == 200 and data.get("type") != "disambiguation":
                summary = data.get("extract")
                if summary:
                    results.append({
                        "term": word,
                        "definition": summary
                    })
        except Exception as e:
            print(f"Error processing {word}: {e}")
            continue

    return results


def extract_core_topic(text, sentence_limit=2):
    """
    Extracts the core topic from a summary using TF-IDF on the first few sentences.
    """
    import re
    from sklearn.feature_extraction.text import TfidfVectorizer

    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    intro = " ".join(sentences[:sentence_limit])

    vectorizer = TfidfVectorizer(stop_words='english', max_features=5)
    X = vectorizer.fit_transform([intro])
    keywords = vectorizer.get_feature_names_out()

    # Return most relevant keyword or fallback
    return keywords[0] if len(keywords) > 0 else "biology"


def search_youtube_videos(query, max_results=3):
    """
    Searches YouTube using the exact user query.
    Filters out non-English and non-educational videos.
    Prioritizes biology-related educational content.
    """
    from googleapiclient.discovery import build
    import logging
    import re

    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

        # Refine the query to explicitly target biology education
        enhanced_query = f"{query.strip()} in biology A-Level structure function lecture tutorial explained"

        request = youtube.search().list(
            q=enhanced_query,
            part="snippet",
            type="video",
            maxResults=10,
            relevanceLanguage="en"
        )
        response = request.execute()

        def extract_video_info(item):
            return {
                "title": item["snippet"]["title"],
                "link": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                "channel": item["snippet"]["channelTitle"],
                "thumbnail": item["snippet"]["thumbnails"]["default"]["url"]
            }

        def is_english(text):
            cleaned = re.sub(r'[^a-zA-Z0-9\s.,!?\'"-]', '', text)
            return len(cleaned) / max(len(text), 1) > 0.8

        def is_educational(item):
            title = item["snippet"]["title"].lower()
            description = item["snippet"].get("description", "").lower()
            channel = item["snippet"]["channelTitle"].lower()

            educational_keywords = [
                "class", "lecture", "tutorial", "chapter", "unit", "grade",
                "a-level", "as level", "biology", "explained", "introduction",
                "education", "study", "revision", "notes", "course", "syllabus",
                "concept", "lesson", "academy", "school", "teacher", "student",
                "explanation", "diagram", "function", "structure", "how it works"
            ]

            return any(kw in title or kw in description or kw in channel for kw in educational_keywords)

        filtered = []
        seen_ids = set()

        for item in response.get("items", []):
            title = item["snippet"]["title"]
            description = item["snippet"].get("description", "")
            video_id = item["id"]["videoId"]

            if (
                video_id not in seen_ids and
                is_english(title + " " + description) and
                is_educational(item)
            ):
                filtered.append(extract_video_info(item))
                seen_ids.add(video_id)

            if len(filtered) >= max_results:
                break

        return filtered

    except Exception as e:
        logging.error(f"Error fetching YouTube videos: {e}")
        return []
