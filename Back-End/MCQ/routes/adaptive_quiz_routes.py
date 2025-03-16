import uuid
import logging
import time
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends
from utils.user_mgmt_methods import get_current_user
from database.database import quizzes_collection, users_collection
from utils.quiz_generation_methods import fetch_questions_from_db, get_irt_based_difficulty_distribution
from utils.generate_question import generate_mcq_based_on_performance
import traceback
import sys

router = APIRouter()

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@router.get("/generate_adaptive_mcqs/{user_id}/{question_count}")
def generate_next_quiz(user_id: str, question_count: int, current_user: str = Depends(get_current_user)):
    """Generate a new adaptive quiz based on user's previous performance."""
    try:
        logging.info(f"📝 Starting adaptive quiz generation for user {user_id} with {question_count} questions...")
        sys.stdout.flush()  # Force log flushing

        existing_user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not existing_user:
            logging.error("❌ User not found")
            sys.stdout.flush()
            raise HTTPException(status_code=404, detail="User not found. Please register before generating a quiz.")
        
        if current_user != user_id:
            logging.error("❌ Unauthorized access")
            sys.stdout.flush()
            raise HTTPException(status_code=403, detail="Unauthorized access")

        logging.info("✅ User found, fetching past performance...")
        sys.stdout.flush()

        difficulty_distribution = get_irt_based_difficulty_distribution(user_id, question_count)
        logging.info(f"📊 Difficulty distribution: {difficulty_distribution}")
        sys.stdout.flush()

        current_quiz_questions = set()
        mcqs = []

        for difficulty, count in difficulty_distribution.items():
            generated = 0
            failed_attempts = 0  
            while generated < count:
                logging.info(f"⚙️ Generating MCQ (Difficulty: {difficulty}) - Attempt {generated + 1}/{count}")
                sys.stdout.flush()

                mcq = generate_mcq_based_on_performance(user_id, difficulty)

                logging.info(f"📩 Received MCQ response: {mcq}")
                sys.stdout.flush()

                if not mcq or not isinstance(mcq, dict) or "question" not in mcq:
                    failed_attempts += 1
                    logging.warning(f"⚠️ Failed MCQ generation for {difficulty}. Retrying... ({failed_attempts}/3)")
                    sys.stdout.flush()

                    if failed_attempts >= 3:
                        logging.error(f"❌ Skipping {difficulty} MCQ after 3 failed attempts.")
                        sys.stdout.flush()
                        break  # Move to the next difficulty level
                    
                    continue  # Retry another question
                
                mcq_text = mcq["question"]

                if mcq_text in current_quiz_questions:
                    logging.warning(f"🚫 Duplicate detected: {mcq_text}, retrying...")
                    failed_attempts += 1
                    sys.stdout.flush()
                    continue

                formatted_mcq = {
                    "question_text": mcq_text,
                    "option1": mcq.get("options", {}).get("A", "N/A"),
                    "option2": mcq.get("options", {}).get("B", "N/A"),
                    "option3": mcq.get("options", {}).get("C", "N/A"),
                    "option4": mcq.get("options", {}).get("D", "N/A"),
                    "option5": mcq.get("options", {}).get("E", "N/A"),
                    "correct_answer": mcq.get("correct_answer", "N/A"),
                    "difficulty": difficulty
                }

                mcqs.append(formatted_mcq)
                current_quiz_questions.add(mcq_text)
                generated += 1
                sys.stdout.flush()

        if len(mcqs) < question_count:
            remaining_needed = question_count - len(mcqs)
            logging.warning(f"⚠ Not enough questions generated. Fetching {remaining_needed} from DB.")
            sys.stdout.flush()

            db_questions = fetch_questions_from_db(remaining_needed)
            mcqs.extend(db_questions)

        quiz_id = str(uuid.uuid4())
        quiz_data = {
            "quiz_id": quiz_id,
            "user_id": user_id,
            "difficulty_distribution": difficulty_distribution,
            "questions": mcqs,
            "created_at": time.time(),
        }

        logging.info("🛠️ Saving quiz to the database...")
        sys.stdout.flush()
        quizzes_collection.insert_one(quiz_data)
        
        logging.info(f"✅ Quiz generated successfully! Quiz ID: {quiz_id}")
        sys.stdout.flush()

        return {"quiz_id": quiz_id, "total_questions": len(mcqs), "mcqs": mcqs}

    except Exception as e:
        logging.error(f"🔥 Error generating adaptive quiz: {str(e)}")
        logging.error(traceback.format_exc())
        sys.stdout.flush()
        raise HTTPException(status_code=500, detail=str(e))