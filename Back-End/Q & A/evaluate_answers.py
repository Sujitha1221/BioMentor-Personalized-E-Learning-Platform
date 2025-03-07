import logging
from sentence_transformers import SentenceTransformer, models
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity as cosine
from rapidfuzz.distance import Levenshtein
import spacy
from datetime import datetime
from pymongo import MongoClient
from language_tool_python import LanguageTool
from generate_answers import generate_structured_answer, generate_essay_answer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

# MongoDB Connection
def get_db():
    """
    Connect to MongoDB and return the database object.
    """
    try:
        client = MongoClient("mongodb://localhost:27017/")  # Update with your MongoDB URI
        db = client["evaluation_db"]
        logging.info("Connected to MongoDB successfully.")
        return db
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {e}", exc_info=True)
        raise

db = get_db()

# Save Evaluation Data
def save_evaluation(student_id, question, question_type, user_answer, model_answer, evaluation_result):
    """
    Save evaluation data to MongoDB.
    """
    try:
        collection = db["evaluations"]
        record = {
            "student_id": student_id,
            "question": question,
            "question_type": question_type,
            "user_answer": user_answer,
            "model_answer": model_answer,
            "evaluation_result": evaluation_result,
            "timestamp": datetime.utcnow()
        }
        collection.insert_one(record)
        logging.info(f"Evaluation data saved for student_id: {student_id}")
    except Exception as e:
        logging.error(f"Error saving evaluation data: {e}", exc_info=True)
        raise
    
# Load SciBERT for semantic similarity
def load_scibert_model():
    """
    Wrap SciBERT in SentenceTransformer with pooling layers.
    """
    logging.info("Loading SciBERT model...")
    word_embedding_model = models.Transformer('allenai/scibert_scivocab_uncased')
    pooling_model = models.Pooling(
        word_embedding_model.get_word_embedding_dimension(),
        pooling_mode_mean_tokens=True
    )
    model = SentenceTransformer(modules=[word_embedding_model, pooling_model])
    logging.info("SciBERT model loaded successfully.")
    return model

scibert_model = load_scibert_model()

# Load spaCy model for keyword extraction
logging.info("Loading spaCy model...")
nlp = spacy.load("en_core_web_sm")
logging.info("spaCy model loaded successfully.")

# Initialize LanguageTool for grammar checking
logging.info("Initializing LanguageTool for grammar checking...")
tool = LanguageTool('en-US')
logging.info("LanguageTool initialized successfully.")

# Function to calculate semantic similarity using SciBERT
def semantic_similarity_scibert(text1, text2):
    """
    Compute semantic similarity between two texts using SciBERT.
    """
    logging.info(f"Calculating SciBERT semantic similarity between: '{text1}' and '{text2}'")
    embeddings = scibert_model.encode([text1, text2])
    similarity = cosine([embeddings[0]], [embeddings[1]])[0][0]
    logging.info(f"SciBERT similarity score: {similarity}")
    return similarity

# Function to calculate TF-IDF cosine similarity
def tfidf_cosine_similarity(text1, text2):
    """
    Compute cosine similarity between two texts using TF-IDF vectors.
    """
    logging.info("Calculating TF-IDF cosine similarity...")
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text1, text2])
    similarity = cosine(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    logging.info(f"TF-IDF similarity score: {similarity}")
    return similarity

# Function to extract keywords using spaCy
def extract_keywords(text):
    """
    Extract keywords (nouns, proper nouns, and verbs) from the text.
    """
    logging.info(f"Extracting keywords from text: '{text}'")
    doc = nlp(text)
    keywords = {token.text.lower() for token in doc if token.pos_ in {"NOUN", "PROPN", "VERB"}}
    logging.info(f"Keywords extracted: {keywords}")
    return keywords

# Function to calculate Jaccard similarity
def jaccard_similarity(set1, set2):
    """
    Compute Jaccard similarity between two sets.
    """
    logging.info("Calculating Jaccard similarity...")
    similarity = len(set1 & set2) / len(set1 | set2) if set1 | set2 else 0
    logging.info(f"Jaccard similarity score: {similarity}")
    return similarity

# Function to calculate hybrid similarity
def hybrid_similarity(user_answer, model_answer, weights=None):
    """
    Compute a hybrid similarity score combining SciBERT, TF-IDF, and Jaccard metrics.
    """
    logging.info("Calculating hybrid similarity...")
    if weights is None:
        weights = {"scibert": 0.5, "tfidf": 0.3, "jaccard": 0.2}  # Default weights

    scibert_score = float(semantic_similarity_scibert(user_answer, model_answer))
    tfidf_score = float(tfidf_cosine_similarity(user_answer, model_answer))
    user_keywords = extract_keywords(user_answer)
    model_keywords = extract_keywords(model_answer)
    jaccard_score = float(jaccard_similarity(user_keywords, model_keywords))

    final_score = (
        weights["scibert"] * scibert_score +
        weights["tfidf"] * tfidf_score +
        weights["jaccard"] * jaccard_score
    )

    logging.info(f"Hybrid similarity scores - Final: {final_score}, SciBERT: {scibert_score}, TF-IDF: {tfidf_score}, Jaccard: {jaccard_score}")
    return {
        "final_score": float(final_score),
        "scibert_score": scibert_score,
        "tfidf_score": tfidf_score,
        "jaccard_score": jaccard_score,
    }

# Function to check grammar using LanguageTool
def check_grammar(text):
    """
    Check grammar and spelling using LanguageTool.
    Returns the number of errors and suggestions for improvement.
    """
    logging.info(f"Checking grammar for text: '{text}'")
    matches = tool.check(text)
    errors = len(matches)
    suggestions = [
        f"Suggested Correction: {', '.join(match.replacements)}"
        for match in matches if match.replacements
    ]
    logging.info(f"Grammar check - Errors: {errors}, Suggestions: {suggestions}")
    return {
        "errors": errors,
        "suggestions": suggestions
    }

# Function to evaluate the user's answer
def evaluate_answer_hybrid(user_answer, model_answer):
    """
    Evaluate the user's answer using a hybrid similarity model, grammar, and keyword analysis.
    """
    logging.info("Evaluating user's answer...")
    # Step 1: Hybrid similarity
    similarity_scores = hybrid_similarity(user_answer, model_answer)
    semantic_score = float(similarity_scores["final_score"])

    # Step 2: Keyword comparison
    user_keywords = extract_keywords(user_answer)
    model_keywords = extract_keywords(model_answer)
    jaccard_score = float(jaccard_similarity(user_keywords, model_keywords))

    # Step 3: Grammar check
    grammar_results = check_grammar(user_answer)
    grammar_score = float(max(1 - grammar_results["errors"] / 10, 0))

    # Step 4: Final weighted score
    final_score = float(0.6 * semantic_score + 0.25 * jaccard_score + 0.15 * grammar_score)

    logging.info(f"Evaluation completed. Final score: {final_score}")
    return {
        "final_score": round(final_score * 100, 2),
        "semantic_score": round(similarity_scores["scibert_score"] * 100, 2),
        "tfidf_score": round(similarity_scores["tfidf_score"] * 100, 2),
        "jaccard_score": round(jaccard_score * 100, 2),
        "grammar_score": round(grammar_score * 100, 2),
        "feedback": {
            "missing_keywords": list(model_keywords - user_keywords),
            "extra_keywords": list(user_keywords - model_keywords),
            "grammar_suggestions": grammar_results["suggestions"]
        },
    }

def evaluate_user_answer(student_id, question, user_answer, question_type):
    """
    Evaluates the user's answer against a generated model answer based on the question type.
    """
    logging.info(f"Evaluating user's answer. Question: '{question}', Question Type: '{question_type}'")
    try:
        if question_type == "structured":
            # Generate a structured answer
            logging.info("Generating structured model answer...")
            model_answer = generate_structured_answer(
                query=question,
                k=3,  # Default k for structured
                max_words=50  # Default max words for structured
            )
            logging.info("Structured model answer generated successfully.")
        elif question_type == "essay":
            # Generate an essay-style answer
            logging.info("Generating essay model answer...")
            model_answer = generate_essay_answer(
                query=question,
                k=5,  # Default k for essay
                min_words=175,  # Default min words for essay
                max_words=300  # Default max words for essay
            )
            logging.info("Essay model answer generated successfully.")
        else:
            # Invalid question type
            logging.error(f"Invalid question type: {question_type}")
            raise ValueError("Invalid question type. Use 'structured' or 'essay'.")

        # Evaluate the user's answer against the generated model answer
        logging.info("Evaluating user's answer against the model answer...")
        result = evaluate_answer_hybrid(user_answer, model_answer)
        logging.info("Evaluation completed successfully.")
        
        # Save evaluation result
        save_evaluation(student_id, question, question_type, user_answer, model_answer, result)

        return {
            "question": question,
            "question_type": question_type,
            "user_answer": user_answer,
            "model_answer": model_answer,
            "evaluation_result": result
        }
    except Exception as e:
        logging.error(f"Error occurred while evaluating user's answer: {e}", exc_info=True)
        raise


# Example Usage
if __name__ == "__main__":
    user_answer = "Photosynthesis produces glucos using sunligt and waterr."
    model_answer = "Photosynthesis is a process where plants use sunlight, water, and carbon dioxide to produce glucose and oxygen."

    logging.info("Running example evaluation...")
    result = evaluate_answer_hybrid(user_answer, model_answer)

    logging.info("Evaluation result:")
    logging.info(f"Final Score: {result['final_score']}")
    logging.info(f"Semantic Similarity Score: {result['semantic_score']}")
    logging.info(f"TF-IDF Score: {result['tfidf_score']}")
    logging.info(f"Jaccard Similarity Score: {result['jaccard_score']}")
    logging.info(f"Grammar Score: {result['grammar_score']}")
    logging.info(f"Feedback: {result['feedback']}")