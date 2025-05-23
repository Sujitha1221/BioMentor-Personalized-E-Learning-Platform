import uuid
import logging
import time
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends
from utils.user_mgmt_methods import get_current_user
from database.database import users_collection, quizzes_collection
from utils.quiz_generation_methods import fetch_questions_from_db, get_irt_based_difficulty_distribution, get_seen_questions
from utils.generate_question import generate_mcq_based_on_performance
import traceback
import sys
import numpy as np
from utils.model_loader import embedding_model
from threading import Thread
from utils.answer_verifier import verify_quiz_answers_async 

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
            logging.error("User not found")
            sys.stdout.flush()
            raise HTTPException(status_code=404, detail="User not found. Please register before generating a quiz.")
        
        if current_user != user_id:
            logging.error("Unauthorized access")
            sys.stdout.flush()
            raise HTTPException(status_code=403, detail="Unauthorized access")

        difficulty_distribution = get_irt_based_difficulty_distribution(user_id, question_count)
        logging.info(f"📊 Difficulty distribution: {difficulty_distribution}")
        sys.stdout.flush()
        
        # 🧠 Cache past questions once
        past_questions = get_seen_questions(user_id)
        past_embeddings = (
            embedding_model.encode(past_questions).astype(np.float32)
            if past_questions else None
        )

        current_quiz_questions = set()
        mcqs = []

        for difficulty, count in difficulty_distribution.items():
            generated = 0
            failed_attempts = 0  
            while generated < count and failed_attempts < 5:
                logging.info(f"⚙️ Generating MCQ (Difficulty: {difficulty}) - Attempt {generated + 1}/{count}")
                sys.stdout.flush()

                batch_mcqs = generate_mcq_based_on_performance(user_id, difficulty,  existing_questions=current_quiz_questions, past_embeddings=past_embeddings)

                logging.info(f"📩 Received MCQ response: {batch_mcqs}")
                sys.stdout.flush()

                if not batch_mcqs:
                    failed_attempts += 1
                    logging.warning(f"⚠ No MCQs received. Retrying... ({failed_attempts}/5)")
                    continue

                for mcq in batch_mcqs:
                    q_text = mcq.get("question", "")
                    if not q_text or q_text in current_quiz_questions:
                        continue

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
                    generated += 1 
                    sys.stdout.flush()
                
                    if generated >= count:
                        break 

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
        Thread(target=verify_quiz_answers_async, args=(quiz_id,)).start()
        
        logging.info(f" Quiz generated successfully! Quiz ID: {quiz_id}")
        sys.stdout.flush()

        return {"quiz_id": quiz_id, "total_questions": len(mcqs), "mcqs": mcqs}

    except Exception as e:
        logging.error(f" Error generating adaptive quiz: {str(e)}")
        logging.error(traceback.format_exc())
        sys.stdout.flush()
        raise HTTPException(status_code=500, detail=str(e))