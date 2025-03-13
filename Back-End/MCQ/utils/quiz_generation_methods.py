import random
from routes.response_routes import estimate_student_ability
import logging
import faiss
import numpy as np
import pandas as pd
from bson import ObjectId
from database.database import quizzes_collection
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Track seen questions to avoid duplicates
seen_questions = set()

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load Sentence Transformer model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Load FAISS index and dataset
index = faiss.read_index("dataset/question_embeddings.index")
embeddings_matrix = np.load("dataset/question_embeddings.npy")
dataset = pd.read_csv("dataset/question_dataset_with_clusters.csv")

# Method to retrieve diverse context questions to generate new questions
def retrieve_context_questions(query_text, top_k=3):
    """Retrieve diverse MCQs from different clusters to blend context for a new question."""
    query_vector = embedding_model.encode([query_text]).astype(np.float32)
    
    # Ensure FAISS index isn't empty before searching
    if index.ntotal == 0:
        logging.warning("⚠ FAISS index is empty! No previous questions available.")
        return pd.DataFrame()

    D, I = index.search(query_vector, k=min(top_k, index.ntotal))  # Retrieve top-K closest MCQs

    # 🔥 FIX: Ensure valid indices
    valid_indices = [i for i in I[0] if 0 <= i < len(dataset)]
    if not valid_indices:
        logging.warning("⚠ No valid indices found in FAISS search. Returning empty DataFrame.")
        return pd.DataFrame()

    retrieved_questions = dataset.iloc[valid_indices]

    # Ensure selection from different clusters
    unique_clusters = set()
    context_questions = []

    for _, row in retrieved_questions.iterrows():
        if row["Cluster"] not in unique_clusters:
            context_questions.append(row)
            unique_clusters.add(row["Cluster"])
        if len(context_questions) >= top_k:
            break

    if not context_questions:
        logging.warning("⚠ No diverse context questions found.")
        return pd.DataFrame()

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

# Method to check if a question is too similar to existing ones
def is_question_too_similar(new_question, threshold=0.8):
    """Check if a generated MCQ is too similar to existing ones using FAISS & text similarity."""
    query_vector = embedding_model.encode([new_question]).astype(np.float32)
    
    if index.ntotal == 0:
        return False  # No stored questions, so no risk of duplicates
    
    # 🔹 Step 1: FAISS Similarity Search
    D, I = index.search(query_vector, k=3)  # Retrieve top-3 closest MCQs
    similarity_score = 1 / (1 + D[0][0])  # Convert L2 distance to similarity

    if similarity_score > threshold:
        return True  # Already too similar based on FAISS
    
    # 🔹 Step 2: Text-Based Cosine Similarity (To detect reworded questions)
    similar_questions = [dataset.iloc[i]["Question Text"] for i in I[0] if 0 <= i < len(dataset)]
    similar_vectors = embedding_model.encode(similar_questions)
    new_vector = embedding_model.encode([new_question])

    cosine_sim = cosine_similarity(new_vector, similar_vectors).max()
    
    return cosine_sim > 0.85  # Adjust threshold as needed

def is_similar_to_same_quiz_questions(new_question, generated_questions, threshold=0.75):
    """Check if the generated question is similar to any question already generated in the same quiz."""
    
    if not generated_questions:
        return False  # ✅ If no questions exist, return False (not similar)
    
    new_vector = embedding_model.encode([new_question]).astype(np.float32)
    existing_vectors = embedding_model.encode(list(generated_questions)).astype(np.float32)

    # 🔹 Compute cosine similarity with all previous questions in the same quiz
    similarity_scores = cosine_similarity(new_vector, existing_vectors)[0]
    
    # ✅ Return True if **any** question in the same quiz is too similar
    if any(sim >= threshold for sim in similarity_scores):
        logging.warning(f"🚫 Too Similar to Same Quiz Questions: {new_question} (Max Cosine Sim: {max(similarity_scores)})")
        return True  

    return False

def is_similar_to_past_quiz_questions(new_question, user_id, threshold=0.75):
    """Check if the generated question is similar to any question from past quizzes of the same user."""
    
    seen_questions = get_seen_questions(user_id)
    
    if not seen_questions:
        return False  # ✅ If no past questions exist, return False (not similar)

    new_vector = embedding_model.encode([new_question]).astype(np.float32)
    past_vectors = embedding_model.encode(list(seen_questions)).astype(np.float32)

    # 🔹 Compute cosine similarity with all past questions
    similarity_scores = cosine_similarity(new_vector, past_vectors)[0]

    # ✅ Return True if **any** past question is too similar
    if any(sim >= threshold for sim in similarity_scores):
        logging.warning(f"🚫 Too Similar to Past Quiz Questions: {new_question} (Max Cosine Sim: {max(similarity_scores)})")
        return True  

    return False

# Method to get IRT-based difficulty distribution for a user
def get_irt_based_difficulty_distribution(user_id, total_questions):
    """Dynamically adjusts quiz difficulty based on user performance trend."""
    theta = estimate_student_ability(user_id)
    
    # 🔹 Get user's last 5 quiz difficulties
    recent_quizzes = list(quizzes_collection.find(
        {"user_id": ObjectId(user_id)},
        {"difficulty_distribution": 1}
    ).sort("created_at", -1).limit(5))

    if recent_quizzes:
        avg_difficulty = np.mean([quiz["difficulty_distribution"].get("medium", 0) for quiz in recent_quizzes])
    else:
        avg_difficulty = 0.4  # Default to 40% medium if no past data
    
    # 🔹 Adjust difficulty ratios based on trend
    if theta > 1.5:  
        easy_ratio, medium_ratio, hard_ratio = 0.05, avg_difficulty, 0.55
    elif theta > 0.5:  
        easy_ratio, medium_ratio, hard_ratio = 0.15, avg_difficulty, 0.4
    elif theta < -0.5:  
        easy_ratio, medium_ratio, hard_ratio = 0.5, avg_difficulty, 0.2
    else:
        easy_ratio, medium_ratio, hard_ratio = 0.3, avg_difficulty, 0.3
    logging.info(f"📊 IRT Difficulty Ratios: Easy={round(easy_ratio * total_questions)}, Medium={round(medium_ratio * total_questions)}, Hard={total_questions - (round(easy_ratio * total_questions) + round(medium_ratio * total_questions))}")
    return {
        "easy": round(easy_ratio * total_questions),
        "medium": round(medium_ratio * total_questions),
        "hard": total_questions - (round(easy_ratio * total_questions) + round(medium_ratio * total_questions))
    }

# Method to get previous quiz questions of a user
def get_seen_questions(user_id):
    """Retrieve previously seen questions and exclude similar ones."""
    
    seen_questions = set()
    
    # 🔹 Fetch past quizzes from the database
    past_quizzes = list(quizzes_collection.find(
        {"user_id": user_id},
        {"questions.question_text": 1, "_id": 0}  
    ))

    logging.info(f"🔍 Found {len(past_quizzes)} past quizzes for user {user_id}")

    for quiz in past_quizzes:
        if "questions" in quiz:
            for question in quiz["questions"]:
                if "question_text" in question:  # ✅ Ensure field exists
                    seen_questions.add(question["question_text"])

    # logging.info(f"🔍 Fetched {len(seen_questions)} unique questions from past quizzes: {seen_questions}")
    return seen_questions


# Method to filter out similar questions from the seen questions
def filter_similar_questions(new_questions, seen_questions, threshold=0.8):
    """Remove questions that are too similar to seen questions using FAISS similarity."""
    unique_questions = []
    
    for question in new_questions:
        is_similar = False
        new_vector = embedding_model.encode([question]).astype(np.float32)

        for seen_question in seen_questions:
            seen_vector = embedding_model.encode([seen_question]).astype(np.float32)
            
            # Compute cosine similarity
            similarity_score = cosine_similarity(new_vector, [seen_vector])[0][0]

            if similarity_score > threshold:  # If similarity is too high, reject
                is_similar = True
                break
        
        if not is_similar:
            unique_questions.append(question)

    return unique_questions

