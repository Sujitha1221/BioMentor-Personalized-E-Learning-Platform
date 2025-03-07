import uuid
import logging
import requests
import random
import time
from fastapi import APIRouter, HTTPException
from database.database import quizzes_collection  # Import MongoDB collection

router = APIRouter()

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Google Colab API Endpoint
COLAB_API_URL = "https://d098-34-125-57-71.ngrok-free.app/generate_mcq"

# Define difficulty levels
DIFFICULTY_DISTRIBUTION = {"easy": 5, "medium": 5, "hard": 5}

# Track seen questions to avoid duplicates
seen_questions = set()

def is_similar(q1, q2, threshold=0.85):
    """Check if two questions are too similar."""
    from difflib import SequenceMatcher
    return SequenceMatcher(None, q1, q2).ratio() > threshold

def add_unique_question(mcq):
    """Adds a question if it's not too similar to existing ones."""
    for q in seen_questions:
        if is_similar(mcq["question"], q):
            logging.warning(f"⚠ Too Similar: {mcq['question']}")
            return False  # Skip adding
    seen_questions.add(mcq["question"])
    return True

def generate_mcq(difficulty, max_retries=3):
    """Generates an MCQ and ensures uniqueness and correctness."""
    retries = 0

    while retries < max_retries:
        prompt = f"""
        Generate a **{difficulty}** level multiple-choice biology question.

        **Requirements:**
        - Must be a completely new and unique question.
        - Must contain exactly **5 unique answer choices** labeled **A-E**.
        - Must explicitly state the correct answer.
        - The correct answer must be **one of the provided choices**.

        **Format:**
        ```
        Question: <Generated Question>
        A) <Option A>
        B) <Option B>
        C) <Option C>
        D) <Option D>
        E) <Option E>
        Correct Answer: <A/B/C/D/E>
        ```
        """

        try:
            response = requests.post(COLAB_API_URL, json={"prompt": prompt}, timeout=30)
            data = response.json()

            if "mcq" not in data or not isinstance(data["mcq"], dict):
                logging.warning(f"⚠ Invalid API response: {data}")
                retries += 1
                continue

            question_data = data["mcq"]

            # Ensure valid question text
            if not question_data.get("question") or question_data.get("question") == "<Generated Question>":
                logging.warning(f"⚠ Malformed MCQ (missing question text): {question_data}")
                retries += 1
                continue

            # Ensure answer choices are unique
            options = question_data.get("options", {})
            if len(set(options.values())) < 5:  # Duplicate options exist
                logging.warning(f"⚠ Duplicate answers detected: {options}")
                retries += 1
                continue

            # Ensure correct answer is valid
            correct_answer = question_data.get("correct_answer", "").strip()
            answer_choices = ["A", "B", "C", "D", "E"]
            if correct_answer not in answer_choices or options.get(correct_answer, "") not in options.values():
                logging.warning(f"⚠ Correct answer mismatch: {correct_answer} not in {options}")
                retries += 1
                continue

            # Ensure question uniqueness
            if not add_unique_question(question_data):
                retries += 1
                continue

            # ✅ Add difficulty to each question
            question_data["difficulty"] = difficulty

            logging.info(f"✅ Successfully generated MCQ: {question_data['question']}")
            return question_data

        except requests.exceptions.RequestException as e:
            logging.error(f"⚠ API Error: {e}")
            retries += 1

    return None

@router.get("/generate_mcqs/{user_id}")
def generate_quiz(user_id: str):
    """Generates exactly 15 MCQs (5 Easy, 5 Medium, 5 Hard), stores in DB, and returns to user."""
    try:
        logging.info(f"📝 Generating quiz for user {user_id}...")
        quiz_id = str(uuid.uuid4())  # Unique quiz session ID
        mcqs = []

        for difficulty, count in DIFFICULTY_DISTRIBUTION.items():
            generated = 0
            while generated < count:
                mcq = generate_mcq(difficulty)
                if mcq:
                    formatted_mcq = {
                        "question_text": mcq["question"],
                        "option1": mcq["options"]["A"],
                        "option2": mcq["options"]["B"],
                        "option3": mcq["options"]["C"],
                        "option4": mcq["options"]["D"],
                        "option5": mcq["options"]["E"],
                        "correct_answer": mcq["correct_answer"],
                        "difficulty": difficulty,
                    }
                    mcqs.append(formatted_mcq)
                    generated += 1

        quiz_data = {
            "quiz_id": quiz_id,
            "user_id": user_id,
            "difficulty_distribution": DIFFICULTY_DISTRIBUTION,
            "questions": mcqs,
            "created_at": time.time(),
        }
        quizzes_collection.insert_one(quiz_data)

        return {"quiz_id": quiz_id, "total_questions": len(mcqs), "mcqs": mcqs}

    except Exception as e:
        logging.critical(f"🔥 Fatal Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
