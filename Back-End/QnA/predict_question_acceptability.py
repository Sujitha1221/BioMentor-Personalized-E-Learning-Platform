from gradio_client import Client
import re
import logging
from better_profanity import profanity
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import spacy
from transformers import pipeline

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

    return True, "Your question is acceptable."

# Example usage
if __name__ == "__main__":
    sample_question = "How to make a harmless prank at school?."
    is_acceptable = moderate_question(sample_question)
    logging.info("Acceptable" if is_acceptable else "Not Acceptable")
    logging.info(is_acceptable)

