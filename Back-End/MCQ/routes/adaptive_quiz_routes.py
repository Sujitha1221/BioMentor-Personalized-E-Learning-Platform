import uuid
import logging
import time
from bson import ObjectId
from fastapi import APIRouter, HTTPException
from database.database import quizzes_collection, users_collection
from utils.quiz_generation_methods import get_seen_questions, filter_similar_questions, get_irt_based_difficulty_distribution
from utils.generate_question import generate_mcq_based_on_performance

router = APIRouter()

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@router.get("/generate_adaptive_mcqs/{user_id}/{question_count}")
def generate_next_quiz(user_id: str, question_count: int):
    """
    Generate a new adaptive quiz based on user's previous performance.
    Instead of selecting from a pre-existing database, new questions are generated dynamically.
    """
    try:
        existing_user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found. Please register before generating a quiz.")

        # ✅ Fetch user's past performance
        difficulty_distribution = get_irt_based_difficulty_distribution(user_id, question_count)
        seen_questions = get_seen_questions(user_id)
        mcqs = []

        for difficulty, count in difficulty_distribution.items():
            generated = 0
            failed_attempts = 0  
            while generated < count:
                # ✅ Generate new question dynamically based on user performance
                mcq = generate_mcq_based_on_performance(user_id, difficulty)
                
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
                
                # ✅ Ensure question is unique
                if mcq and mcq["question"] not in seen_questions:
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
                    mcqs.append(formatted_mcq)
                    seen_questions.add(mcq["question"])
                    generated += 1
                    
        # ✅ Ensure questions are unique (Filter out similar ones)
        unique_mcqs = filter_similar_questions([mcq["question_text"] for mcq in mcqs], seen_questions)
        mcqs = [mcq for mcq in mcqs if mcq["question_text"] in unique_mcqs]


        # ✅ Ensure we have the correct number of questions
        if len(mcqs) < question_count:
            remaining_questions_needed = question_count - len(mcqs)
            logging.warning(f"⚠ Not enough new questions generated. Fetching {remaining_questions_needed} from database.")
            
            available_questions = list(quizzes_collection.find({"user_id": user_id}))
            for stored_quiz in available_questions:
                for question in stored_quiz["questions"]:
                    if question["question_text"] not in seen_questions and len(mcqs) < question_count:
                        mcqs.append(question)
                        seen_questions.add(question["question_text"])

        quiz_id = str(uuid.uuid4())  # Unique quiz session ID

        quiz_data = {
            "quiz_id": quiz_id,
            "user_id": user_id,
            "difficulty_distribution": difficulty_distribution,
            "questions": mcqs,
            "created_at": time.time(),
        }

        # ✅ Save the adaptive quiz in quizzes_collection
        quizzes_collection.insert_one(quiz_data)

        return {"quiz_id": quiz_id, "total_questions": len(mcqs), "mcqs": mcqs}

    except Exception as e:
        logging.error(f"🔥 Error generating adaptive quiz: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
