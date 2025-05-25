import uuid
import logging
import time
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends
from utils.user_mgmt_methods import get_current_user
from database.database import quizzes_collection, users_collection
from utils.generate_question import generate_mcq
from threading import Thread
from utils.answer_verifier import verify_quiz_answers_async 

router = APIRouter()

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Define difficulty levels
DIFFICULTY_DISTRIBUTION = {"easy": 8, "medium": 6, "hard": 6}

@router.get("/generate_mcqs/{user_id}")
def generate_quiz(user_id: str, current_user: str = Depends(get_current_user)):
    """Generates exactly 18 MCQs (6 Easy, 6 Medium, 6 Hard), stores in DB, and returns to user."""
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

            while generated < count and failed_attempts < 5:
                batch_mcqs = generate_mcq(difficulty, user_id, existing_questions=current_quiz_questions)

                #  Log response for debugging
                logging.info(f"📩 Received MCQ response: {batch_mcqs}")

                if not batch_mcqs:
                    failed_attempts += 1
                    logging.warning(f"⚠ No MCQs received. Retrying... ({failed_attempts}/5)")
                    continue

                for mcq in batch_mcqs:
                    q_text = mcq.get("question", "")
                    if not q_text or q_text in current_quiz_questions:
                        continue

                    #  Successfully generated a question, add to the list
                    formatted_mcq = {
                        "question_text": q_text,  
                        "option1": mcq.get("options", {}).get("A", "N/A"),
                        "option2": mcq.get("options", {}).get("B", "N/A"),
                        "option3": mcq.get("options", {}).get("C", "N/A"),
                        "option4": mcq.get("options", {}).get("D", "N/A"),
                        "option5": mcq.get("options", {}).get("E", "N/A"),
                        "correct_answer": mcq.get("correct_answer", "N/A"),
                        "difficulty": difficulty
                    }
                    current_quiz_questions.add(q_text)
                    mcqs.append(formatted_mcq)
                    generated += 1  #  Increase count only if a valid MCQ is added
                    
                    if generated >= count:
                        break 

            #  Log how many MCQs were generated per difficulty
            logging.info(f" Successfully generated {generated}/{count} {difficulty}-level MCQs.")

        #  Handle partial quiz generation
        if len(mcqs) < 18:
            logging.warning(f"⚠ Could not generate all 15 questions. Returning {len(mcqs)} instead.")

        #  Store successfully generated quiz in DB
        quiz_data = {
            "quiz_id": quiz_id,
            "user_id": user_id,
            "difficulty_distribution": DIFFICULTY_DISTRIBUTION,
            "questions": mcqs,
            "created_at": time.time(),
        }
        quizzes_collection.insert_one(quiz_data)
        Thread(target=verify_quiz_answers_async, args=(quiz_id,)).start()

        return {"quiz_id": quiz_id, "total_questions": len(mcqs), "mcqs": mcqs}

    except Exception as e:
        logging.critical(f" Unexpected Fatal Error: {str(e)}")

        #  If an error occurs, return the **generated** MCQs instead of crashing
        return {
            "error": "An error occurred while generating the quiz.",
            "quiz_id": quiz_id,
            "total_questions": len(mcqs),
            "mcqs": mcqs  #  Return the questions that were successfully generated
        }

@router.get("/get_quiz/{quiz_id}")
def get_quiz(quiz_id: str):
    """
    Fetch a quiz along with all its questions from quizzes_collection.
    """
    try:
        quiz = quizzes_collection.find_one({"quiz_id": quiz_id})

        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found.")

        # Convert ObjectId to string if needed
        quiz["_id"] = str(quiz["_id"])

        return quiz

    except Exception as e:
        logging.error(f" Error fetching quiz: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving the quiz.")
