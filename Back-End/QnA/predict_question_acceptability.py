import logging
import re
import numpy as np
import faiss
import pandas as pd
import spacy
import torch
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline
from better_profanity import profanity
from sentence_transformers import SentenceTransformer
from gradio_client import Client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

def load_nlp_models():
    """
    Load and initialize NLP models:
    - spaCy for Named Entity Recognition (NER)
    - VADER for sentiment analysis
    - BERT-based classifier for toxic content detection
    """
    logging.info("Loading NLP models...")

    # Load spaCy model for Named Entity Recognition (NER)
    nlp = spacy.load("en_core_web_sm")
    logging.info("spaCy model loaded successfully.")

    # Load VADER sentiment analyzer
    analyzer = SentimentIntensityAnalyzer()
    logging.info("VADER sentiment analyzer initialized.")

    # Load pre-trained BERT-based classifier for toxicity detection
    classifier = pipeline("text-classification", model="unitary/toxic-bert")
    logging.info("BERT-based toxicity classifier loaded.")

    return nlp, analyzer, classifier

# Load models
nlp, analyzer, classifier = load_nlp_models()

logging.info("Loading QA and notes datasets...")
qa_df = pd.read_csv('Notes/cleaned_question_and_answer.csv', encoding='ISO-8859-1')
chunked_notes_df = pd.read_csv('Notes/cleaned_Notes.csv', encoding='ISO-8859-1')

logging.info("Loading embedding model and FAISS index...")
embedder = SentenceTransformer('sentence-transformers/multi-qa-mpnet-base-dot-v1')
index = faiss.read_index('DB/faiss_index.bin')

def is_question_in_syllabus(query: str, k: int = 5) -> bool:
    """
    Check if the question is in syllabus by retrieving top-k matches from the FAISS index.
    If any result is retrieved (from QA or Notes), return True.
    """
    try:
        query_embedding = embedder.encode([query], convert_to_numpy=True).astype('float32')
        distances, indices = index.search(query_embedding, k)

        # If any indices are returned, we assume it's in the syllabus
        if indices is not None and len(indices[0]) > 0:
            logging.info(f"Found {len(indices[0])} related items from FAISS. Considering as in syllabus.")
            return True

        logging.info("No relevant content found in FAISS index.")
        return False
    except Exception as e:
        logging.error(f"Error in syllabus check: {e}", exc_info=True)
        return False


def predict_question_acceptability_gradio(question: str) -> bool:
    """
    Sends a question to the Hugging Face Space and returns True if the most confident
    label is 'Acceptable', otherwise returns False.
    """
    logging.info(f"Sending question for prediction: {question}")
    
    try:
        client = Client("Sajeevan2001/bert-question-moderator")
        result = client.predict(
            question,
            api_name="/predict"
        )

        confidences = result.get("confidences", [])
        if confidences:
            for c in confidences:
                logging.info(f"Label: {c['label']}, Confidence: {c['confidence']:.4f}")
                
            top_label = max(confidences, key=lambda x: x["confidence"])
            logging.info(f"Top prediction: {top_label['label']} ({top_label['confidence']:.4f})")
            return top_label["label"] == "Acceptable"
        else:
            logging.warning("No confidences returned from model.")
            return False

    except Exception as e:
        logging.error(f"Failed to get prediction: {e}")
        return False
    
def contains_inappropriate_content(query):
    """
    Checks if the input query contains:
    - Profanity
    - Dangerous keywords
    - Highly negative sentiment
    - Toxic language (using a BERT model)

    Returns a warning message if the query is inappropriate, otherwise returns False.
    """

    query = query.strip().lower()

    # Profanity Check
    if profanity.contains_profanity(query):
        logging.warning(f"Inappropriate language detected: {query}")
        return "Your input contains inappropriate words. Please rephrase."

    # Sentiment Analysis (VADER)
    sentiment_score = analyzer.polarity_scores(query)["compound"]
    if sentiment_score < -0.6:
        logging.warning(f"Highly negative sentiment detected: {query}")
        return "Your question seems inappropriate. Please rephrase."

    # Machine Learning Toxicity Detection (BERT)
    result = classifier(query)[0]
    if result["label"] == "toxic" and result["score"] > 0.85:
        logging.warning(f"Toxic content detected: {query}")
        return "Your question seems inappropriate. Please rephrase."

    return False

def moderate_question(query: str) -> tuple[bool, str]:
    """
    Integrated moderation pipeline:
    1. Check model prediction (Hugging Face Space)
    2. If acceptable, apply custom content filters
    """
    logging.info(f"🔍 Starting moderation for: {query}")

    if not predict_question_acceptability_gradio(query):
        return False, "Your question does not meet our content guidelines. Please rephrase it."

    # Model passed, now do custom checks
    content_warning = contains_inappropriate_content(query)
    if content_warning:
        return False, content_warning
    
    if not is_question_in_syllabus(query):
        return False, "This question appears to be outside the current syllabus."

    return True, "Your question is acceptable."

# Example usage
if __name__ == "__main__":
    sample_question = "How to make a harmless prank at school?."
    is_acceptable = moderate_question(sample_question)
    logging.info("Acceptable" if is_acceptable else "Not Acceptable")
    logging.info(is_acceptable)

