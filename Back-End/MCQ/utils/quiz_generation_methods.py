import random
from routes.response_routes import estimate_student_ability
import logging
import faiss
import numpy as np
import pandas as pd
import re
from bson import ObjectId
from database.database import quizzes_collection
from utils.model_loader import embedding_model
from sklearn.metrics.pairwise import cosine_similarity

# Track seen questions to avoid duplicates
seen_questions = set()

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load FAISS index and dataset
index = faiss.read_index("dataset/question_embeddings.index")
embeddings_matrix = np.load("dataset/question_embeddings.npy")
dataset = pd.read_csv("dataset/question_dataset_with_clusters.csv")

# Method to retrieve diverse context questions to generate new questions
def retrieve_context_questions(query_text, top_k=3):
    """Retrieve diverse MCQs from different clusters and difficulty levels for better generation context."""
    query_vector = embedding_model.encode([query_text]).astype(np.float32)

    if index.ntotal == 0:
        logging.warning("⚠ FAISS index is empty! No previous questions available.")
        return pd.DataFrame()

    # Retrieve 3x top_k for diversity filtering
    D, I = index.search(query_vector, k=min(top_k * 3, index.ntotal))

    valid_indices = [i for i in I[0] if 0 <= i < len(dataset)]
    retrieved_questions = dataset.iloc[valid_indices]

    unique_clusters = set()
    used_difficulties = set()
    context_questions = []

    for _, row in retrieved_questions.iterrows():
        cluster = row["Cluster"]
        difficulty = row.get("Difficulty Level", "").lower()

        if cluster not in unique_clusters and difficulty not in used_difficulties:
            context_questions.append(row)
            unique_clusters.add(cluster)
            used_difficulties.add(difficulty)

        if len(context_questions) >= top_k:
            break

    if not context_questions:
        logging.warning("⚠ No diverse context questions found.")

    else:
        logging.info("🧠 Context Questions Selected:")
        for row in context_questions:
            logging.info(
                f" - Cluster: {row['Cluster']}, Difficulty: {row.get('Difficulty Level', 'N/A')}, "
                f"Q: {row['Question Text'][:60]}..."
            )

    return pd.DataFrame(context_questions)


# Method to assign difficulty parameter based on student ability
def assign_difficulty_parameter(user_id, difficulty):
    """Assigns a difficulty parameter (b) based on IRT using the user's estimated ability."""
    theta = estimate_student_ability(user_id) or 0.0  # Default if None

    if difficulty == "easy":
        return random.uniform(theta - 1.0, theta - 0.2)
    elif difficulty == "medium":
        return random.uniform(theta - 0.3, theta + 0.3)
    elif difficulty == "hard":
        return random.uniform(theta + 0.2, theta + 1.0)
    return 0

# Method to assign discrimination parameter
def assign_discrimination_parameter():
    """Assigns a discrimination parameter (a) randomly within a reasonable range."""
    return random.uniform(0.5, 2.0)  # Higher a values indicate better question discrimination

def is_similar_to_same_quiz_questions(new_question, existing_questions, threshold=0.85):
    """Check if the new question is too similar to previously generated questions."""
    
    if not existing_questions:
        return False  # No previous questions to compare with
    
    # Encode the new question
    new_vector = embedding_model.encode([new_question]).astype(np.float32)

    # Encode existing questions
    existing_vectors = embedding_model.encode(list(existing_questions)).astype(np.float32)

    # Compute cosine similarity
    similarity_scores = cosine_similarity(new_vector, existing_vectors)[0]

    # Get the max similarity score
    max_similarity = max(similarity_scores) if similarity_scores.size else 0

    # If the similarity score is too high, reject the question
    if max_similarity >= threshold:
        logging.warning(f"⚠ Similarity {max_similarity} exceeds threshold {threshold}. Skipping question: {new_question}")
        return True  

    return False  # Safe to use

def is_similar_to_past_quiz_questions(new_question, user_id, threshold=0.65):
    """Check if the generated question is similar to any question from past quizzes of the same user."""
    
    seen_questions = get_seen_questions(user_id)
    
    if not seen_questions:
        return False  #  If no past questions exist, return False (not similar)

    # Generate embeddings for the new question
    new_vector = embedding_model.encode([new_question]).astype(np.float32).reshape(1, -1)

    # Generate embeddings for past questions (only if questions exist)
    past_vectors = embedding_model.encode(seen_questions).astype(np.float32) if seen_questions else np.array([])
    
    # Handle case where there are no past vectors
    if past_vectors.shape[0] == 0:
        return False  

    # Ensure past vectors are correctly shaped (2D array)
    past_vectors = past_vectors.reshape(len(past_vectors), -1)
    
    # Compute cosine similarity with all past questions
    similarity_scores = cosine_similarity(new_vector, past_vectors)[0]

    # Check if similarity exceeds threshold
    max_sim = max(similarity_scores) if len(similarity_scores) > 0 else 0
    if max_sim >= threshold:
        logging.warning(f"🚫 Too Similar to Past Quiz Questions: {new_question} (Max Cosine Sim: {max_sim})")
        return True  

    return False

# Method to get IRT-based difficulty distribution for a user
def get_irt_based_difficulty_distribution(user_id, total_questions):
    """Dynamically adjusts quiz difficulty based on user performance trend and API success rate."""
    theta = estimate_student_ability(user_id) or 0.0  # Default if None
    
    # 🔹 Fetch recent quiz performance (last 3 quizzes)
    recent_quizzes = list(quizzes_collection.find(
        {"user_id": ObjectId(user_id)},
        {"difficulty_distribution": 1, "questions": 1}
    ).sort("created_at", -1).limit(3))

    # Track how many correct answers per difficulty in recent quizzes
    correct_easy = correct_medium = correct_hard = 0
    total_easy = total_medium = total_hard = 1  # Avoid division by zero
    
    for quiz in recent_quizzes:
        for question in quiz["questions"]:
            difficulty = question.get("difficulty", "medium")
            is_correct = question.get("user_answered_correctly", False)
            
            if difficulty == "easy":
                total_easy += 1
                correct_easy += int(is_correct)
            elif difficulty == "medium":
                total_medium += 1
                correct_medium += int(is_correct)
            elif difficulty == "hard":
                total_hard += 1
                correct_hard += int(is_correct)

    # Compute accuracy per difficulty level
    easy_accuracy = correct_easy / total_easy
    medium_accuracy = correct_medium / total_medium
    hard_accuracy = correct_hard / total_hard

    # Base ratios on user's performance
    if easy_accuracy > 0.8:  # User is doing well on easy
        easy_ratio = 0.1
    elif easy_accuracy < 0.5:
        easy_ratio = 0.4
    else:
        easy_ratio = 0.2

    if medium_accuracy > 0.7:
        medium_ratio = 0.5
    elif medium_accuracy < 0.4:
        medium_ratio = 0.3
    else:
        medium_ratio = 0.4

    if hard_accuracy > 0.6:  # User is improving in hard
        hard_ratio = 0.4
    else:
        hard_ratio = 0.3 if hard_accuracy < 0.4 else 0.2  # Reduce hard if they are failing too much

    # Ensure total = 100%
    total_ratio = easy_ratio + medium_ratio + hard_ratio
    easy_ratio /= total_ratio
    medium_ratio /= total_ratio
    hard_ratio /= total_ratio
    
    return {
        "easy": round(easy_ratio * total_questions),
        "medium": round(medium_ratio * total_questions),
        "hard": total_questions - (round(easy_ratio * total_questions) + round(medium_ratio * total_questions))
    }

# fetch last 2 quizzes of a particular user
def get_seen_questions(user_id, limit=1):
    """
    Retrieve previously seen questions efficiently.
    Instead of fetching all quizzes, we only fetch the last `limit` quizzes.
    """
    seen_questions = []

    # Fetch only the last `limit` quizzes (sorted by newest first)
    past_quizzes = list(quizzes_collection.find(
        {"user_id": user_id},
        {"questions.question_text": 1, "_id": 0}
    ).sort("created_at", -1).limit(limit))  # Fetch only recent quizzes

    logging.info(f"🔍 Found {len(past_quizzes)} recent quizzes for user {user_id}")

    for quiz in past_quizzes:
        for question in quiz.get("questions", []):  # Use `.get()` to avoid KeyErrors
            if "question_text" in question:
                seen_questions.append(question["question_text"])  # Maintain order

    return seen_questions

# fetch random questions from database to use it if model hasn't generated proper questions
def fetch_questions_from_db(count=1):
    """
    Fetch random MCQs from the database as a backup when API-generated MCQs fail.
    """
    try:
        pipeline = [{"$sample": {"size": count}}]  # Random sampling in MongoDB
        questions = list(quizzes_collection.aggregate(pipeline))

        if not questions:
            return []

        formatted_questions = []
        for question in questions:
            for q in question.get("questions", []):  # Get questions from stored quizzes
                formatted_questions.append({
                    "question_text": q.get("question_text", "N/A"),
                    "option1": q.get("option1", "N/A"),
                    "option2": q.get("option2", "N/A"),
                    "option3": q.get("option3", "N/A"),
                    "option4": q.get("option4", "N/A"),
                    "option5": q.get("option5", "N/A"),
                    "correct_answer": q.get("correct_answer", "N/A"),
                    "difficulty": q.get("difficulty", "medium"),
                })
                if len(formatted_questions) >= count:
                    break  # Stop when required count is met

        if not isinstance(formatted_questions, list):
            logging.error(f" Database returned invalid format: {formatted_questions}")
            return []

        return formatted_questions

    except Exception as e:
        logging.error(f" Error fetching backup MCQs from DB: {e}")
        return []
    
def is_duplicate_faiss(new_question, index, threshold=0.85):
    """Check if a newly generated question is too similar to stored FAISS index questions."""

    # Encode the new question into a vector
    new_vector = embedding_model.encode([new_question]).astype(np.float32)

    # Search for the most similar questions in FAISS
    D, I = index.search(new_vector, k=5)  # Retrieve top 5 similar questions

    if len(D[0]) > 0 and min(D[0]) <= (1 - threshold):  # Convert FAISS L2 distance to similarity
        logging.warning(f"⚠ FAISS detected duplicate! Min distance: {min(D[0]):.4f}, Threshold: {1 - threshold:.4f}. Skipping question: {new_question}")
        return True  

    return False  # No duplicate detected
 
def clean_correct_answer(raw):
    # Match only full A–E options surrounded by word boundaries
    letters = re.findall(r"\b[A-E]\b", raw.upper())
    return sorted(set(letters))