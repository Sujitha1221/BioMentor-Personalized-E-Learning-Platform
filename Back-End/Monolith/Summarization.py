import logging
import logging.config
import yaml
from fastapi import FastAPI, UploadFile, Form, HTTPException
from rag import RAGModel
from text_extraction_service import extract_content, clean_text, format_as_paragraph
from voice_service import text_to_speech
from file_handler import save_uploaded_file
from fastapi import BackgroundTasks
import os

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

# Ensure the "uploads" directory exists before saving any files
UPLOADS_DIR = "./uploads"
if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)

@app.post("/process-document/")
async def process_document(file: UploadFile, word_count: int = Form(...)):
    """
    Process a document to extract, summarize, and optionally generate a voice file.
    """
    try:
        logger.info("Processing document upload.")
        file_path = save_uploaded_file(file)
        raw_text = extract_content(file_path)

        if not raw_text.strip():
            logger.warning("No content could be extracted from the document.")
            raise HTTPException(status_code=400, detail="No content could be extracted from the document.")

        # Clean and format the extracted text
        cleaned_text = clean_text(raw_text)
        formatted_text = format_as_paragraph(cleaned_text)

        # Generate a summary
        summary = rag_model.generate_summary_for_long_text(formatted_text, max_words=word_count)

        # Save the summary to a file
        summary_file_path = file_path.replace(".pdf", "_summary.txt").replace(".docx", "_summary.txt").replace(".pptx", "_summary.txt").replace(".txt", "_summary.txt")
        with open(summary_file_path, "w", encoding="utf-8") as summary_file:
            summary_file.write(summary)

        # Generate a voice file for the summary
        audio_file_path = file_path.replace(".pdf", ".mp3").replace(".docx", ".mp3").replace(".pptx", ".mp3").replace(".txt", ".mp3")
        text_to_speech(summary, audio_file_path)

        logger.info("Document processed successfully.")
        return {
            "summary": summary,
            "summary_file": summary_file_path,
            "voice_file": audio_file_path
        }
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail="Failed to process document.")



@app.post("/process-query/")
async def process_query(
    background_tasks: BackgroundTasks,
    query: str = Form(...),
    word_count: int = Form(...)
):
    """
    Retrieve and summarize content based on a specific query.
    """
    try:
        logger.info(f"Processing query: {query}")
        
        # Retrieve relevant texts
        relevant_texts = rag_model.retrieve_relevant_content(query)
        if not relevant_texts:
            logger.warning("No relevant content found for the query.")
            raise HTTPException(status_code=400, detail="No relevant content found for the given query.")
        
        combined_text = " ".join(relevant_texts)

        # Define the task to generate the summary and voice file in the background
        def generate_summary_and_audio_task():
            try:
                # Generate summary
                summary = rag_model.generate_summary_for_long_text(combined_text, max_words=word_count)

                # Save the summary to a file
                summary_file = f"./uploads/{query.replace(' ', '_')}_summary.txt"
                with open(summary_file, "w", encoding="utf-8") as file:
                    file.write(summary)
                logger.info(f"Summary stored at {summary_file}.")

                # Generate and save the MP3 file
                audio_file = f"./uploads/{query.replace(' ', '_')}.mp3"
                text_to_speech(summary, audio_file)
                logger.info(f"Audio file created at {audio_file}.")
            except Exception as e:
                logger.error(f"Error during background summary and audio generation: {e}")

        # Start background task
        background_tasks.add_task(generate_summary_and_audio_task)

        # Ask user if they want to store the retrieved content
        user_choice = input(f"Do you want to store the retrieved content for the query '{query}'? (yes/no): ").strip().lower()
        if user_choice == "yes":
            retrieved_file = f"./uploads/{query.replace(' ', '_')}_retrieved.txt"
            rag_model.store_retrieved_content(relevant_texts, retrieved_file)
            logger.info(f"Retrieved content stored at {retrieved_file}.")
            return {
                "message": f"Retrieved content stored at {retrieved_file}. Summary and audio generation in progress.",
                "retrieved_file": retrieved_file
            }
        else:
            logger.info("User chose not to store the retrieved content.")
            return {
                "message": "User chose not to store the retrieved content. Summary and audio generation in progress."
            }
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail="Failed to process query.")



if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
