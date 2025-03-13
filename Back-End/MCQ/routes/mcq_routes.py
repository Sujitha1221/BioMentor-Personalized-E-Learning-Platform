import uuid
import logging
import time
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends
from utils.user_mgmt_methods import get_current_user
from database.database import quizzes_collection, users_collection
from utils.generate_question import generate_mcq
from utils.quiz_generation_methods import is_similar_to_same_quiz_questions

router = APIRouter()

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Define difficulty levels
DIFFICULTY_DISTRIBUTION = {"easy": 5, "medium": 5, "hard": 5}

@router.get("/generate_mcqs/{user_id}")
def generate_quiz(user_id: str, current_user: str = Depends(get_current_user)):
    """Generates exactly 15 MCQs (5 Easy, 5 Medium, 5 Hard), stores in DB, and returns to user."""
    try:
        existing_user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found. Please register before generating a quiz.")
        
        if current_user != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized access")
    
        logging.info(f"📝 Generating quiz for user {user_id}...")
        quiz_id = str(uuid.uuid4())  # Unique quiz session ID
        mcqs = []
        
        current_quiz_questions = set()

        for difficulty, count in DIFFICULTY_DISTRIBUTION.items():
            generated = 0  
            failed_attempts = 0  

            while generated < count:
                mcq = generate_mcq(difficulty, user_id)

                # ✅ Log response for debugging
                logging.info(f"📩 Received MCQ response: {mcq}")

                # ✅ Validate MCQ before using
                if not mcq or not isinstance(mcq, dict) or "question" not in mcq:
                    failed_attempts += 1
                    logging.warning(f"⚠ Failed MCQ generation for {difficulty}. Retrying... ({failed_attempts}/3)")

                    if failed_attempts >= 3:  # 🔥 Reduced from 5 → 3 retries
                        logging.error(f"❌ Skipping {difficulty} MCQ after 3 failed attempts.")
                        break  # Move to the next difficulty level
                    
                    continue  # Retry another question
                
                # ✅ Check if question is already generated in the same quiz
                if mcq["question"] in current_quiz_questions:
                    logging.warning(f"🚫 Duplicate detected within the same quiz: {mcq['question']}, retrying...")
                    failed_attempts += 1
                    continue
                
                if is_similar_to_same_quiz_questions(mcq["question"], current_quiz_questions, threshold=0.75):
                    logging.warning(f"⚠ Too similar to an existing quiz question: {mcq['question']}, retrying...")
                    failed_attempts += 1
                    continue  

                # ✅ Successfully generated a question, add to the list
                formatted_mcq = {
                    "question_text": mcq.get("question", "N/A"),  
                    "option1": mcq.get("options", {}).get("A", "N/A"),
                    "option2": mcq.get("options", {}).get("B", "N/A"),
                    "option3": mcq.get("options", {}).get("C", "N/A"),
                    "option4": mcq.get("options", {}).get("D", "N/A"),
                    "option5": mcq.get("options", {}).get("E", "N/A"),
                    "correct_answer": mcq.get("correct_answer", "N/A"),
                    "difficulty": difficulty
                }
                current_quiz_questions.add(mcq["question"])
                mcqs.append(formatted_mcq)
                generated += 1  # ✅ Increase count only if a valid MCQ is added

            # ✅ Log how many MCQs were generated per difficulty
            logging.info(f"✅ Successfully generated {generated}/{count} {difficulty}-level MCQs.")

        # ✅ Handle partial quiz generation
        if len(mcqs) < 15:
            logging.warning(f"⚠ Could not generate all 15 questions. Returning {len(mcqs)} instead.")

        # ✅ Store successfully generated quiz in DB
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
        logging.critical(f"🔥 Unexpected Fatal Error: {str(e)}")

        # ✅ If an error occurs, return the **generated** MCQs instead of crashing
        return {
            "error": "An error occurred while generating the quiz.",
            "quiz_id": quiz_id,
            "total_questions": len(mcqs),
            "mcqs": mcqs  # ✅ Return the questions that were successfully generated
        }
