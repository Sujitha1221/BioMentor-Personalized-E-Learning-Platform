import time
import logging
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from fastapi import APIRouter, HTTPException, Depends
from database.database import responses_collection, quizzes_collection, users_collection
from bson import ObjectId
from pydantic import BaseModel
from typing import List
from pymongo.errors import PyMongoError
from utils.user_mgmt_methods import get_current_user
import traceback

router = APIRouter()

# Logging Configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# 🔥 Pydantic Model for Each Response
class QuizResponse(BaseModel):
    question_text: str
    selected_answer: str
    time_taken: float  # ✅ Change this to an integer (was previously str)

# 🔥 Pydantic Model for Submitting Quiz
class SubmitQuizRequest(BaseModel):
    user_id: str
    quiz_id: str
    responses: List[QuizResponse]  # ✅ Expect a list of QuizResponse objects
    
import numpy as np

def estimate_student_ability(user_id):
    """Estimates student ability dynamically using correctness & response time."""
    user_data = users_collection.find_one({"_id": ObjectId(user_id)})
    
    if not user_data or "performance" not in user_data or "history" not in user_data["performance"]:
        return 0  # Default ability score
    
    responses = user_data["performance"]["history"]
    if not responses:
        return 0

    correct_responses = sum([r["is_correct"] for quiz in responses for r in quiz])
    total_responses = sum([len(quiz) for quiz in responses])
    total_time = sum([r["time_taken"] for quiz in responses for r in quiz])

    if total_responses == 0:
        return 0

    # ✅ Compute average response time
    avg_time = total_time / total_responses

    # ✅ Time-Based Penalty System:
    if avg_time < 3:  
        time_penalty = 0.3  # 🚨 Very fast responses (possible guessing)
    elif 3 <= avg_time < 7:  
        time_penalty = 0.2  # ⚠ Slightly too fast  
    elif 7 <= avg_time < 90:  
        time_penalty = 0.0  # ✅ Normal thoughtful response  
    elif 90 <= avg_time < 120:  
        time_penalty = 0.1  # 🕒 Slightly long  
    else:  
        time_penalty = 0.2  # ⏳ Very long (possible distractions, not thinking about the quiz)

    # ✅ Apply IRT-based ability estimation formula with time penalty
    ability = np.log(correct_responses / (total_responses - correct_responses + 1)) - time_penalty

    return round(ability, 2)


def update_user_performance(user_id, responses):
    """Updates the user's accuracy and response time for each difficulty level."""
    user_data = users_collection.find_one({"_id": ObjectId(user_id)})

    if not user_data:
        logging.error(f"❌ User {user_id} not found. Aborting update.")
        raise ValueError(f"User {user_id} not found in the database.") 

    performance = user_data.get("performance", {
        "easy_correct": 0, "easy_total": 0, "easy_time": 0, 
        "medium_correct": 0, "medium_total": 0, "medium_time": 0, 
        "hard_correct": 0, "hard_total": 0, "hard_time": 0, 
        "history": []
    })

    for response in responses:
        difficulty = response["difficulty"]
        is_correct = response["is_correct"]
        time_taken = response["time_taken"]

        performance[f"{difficulty}_total"] += 1
        if is_correct:
            performance[f"{difficulty}_correct"] += 1
        performance[f"{difficulty}_time"] += time_taken

    # ✅ Store last 5 quizzes only
    performance["history"].append(responses)
    if len(performance["history"]) > 5:
        performance["history"].pop(0)

    # ✅ Save accuracy percentages
    for difficulty in ["easy", "medium", "hard"]:
        total = performance[f"{difficulty}_total"]
        if total > 0:
            performance[f"{difficulty}_accuracy"] = round((performance[f"{difficulty}_correct"] / total) * 100, 2)
        else:
            performance[f"{difficulty}_accuracy"] = 0.0  # Avoid division by zero

    try:
        result = users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"performance": performance}})
        
        if result.matched_count == 0:
            logging.error(f"❌ No matching user found for ID {user_id}. Performance update failed.")
            raise ValueError(f"Failed to update performance: No matching user found for ID {user_id}.")

        if result.modified_count == 0:
            logging.warning(f"⚠ Performance data for User {user_id} was not modified. Possible no changes.")
        
        logging.info(f"✅ User performance updated successfully for User {user_id}.")

    except PyMongoError as e:
        logging.error(f"🔥 MongoDB Error updating user performance: {e}")
        raise RuntimeError(f"Database error while updating user performance: {e}")

@router.post("/submit_quiz/")
def submit_quiz(data: SubmitQuizRequest,current_user: str = Depends(get_current_user)):
    """
    API to store user's quiz responses in MongoDB and update their performance dynamically.
    """
    try:
        user_id = data.user_id
        quiz_id = data.quiz_id
        responses = data.responses  
        
        logging.info(f"📩 Received quiz submission: User {user_id}, Quiz {quiz_id}, Responses Count: {len(responses)}")

        existing_user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not existing_user:
            logging.error(f"❌ User {user_id} not found in the database.")
            raise HTTPException(status_code=404, detail="User not found. Please register before generating a quiz.")
        
        if current_user != user_id:
            logging.error(f"🚫 Unauthorized access attempt by {current_user}")
            raise HTTPException(status_code=403, detail="Unauthorized access")
    
        # Fetch quiz to validate responses
        quiz = quizzes_collection.find_one({"quiz_id": quiz_id})
        if not quiz:
            logging.error(f"❌ Quiz {quiz_id} not found in the database.")
            raise HTTPException(status_code=404, detail="Quiz not found.")
        
        # ✅ Check that the quiz was created for this user
        if str(quiz.get("user_id")) != str(user_id):
            raise HTTPException(status_code=403, detail="This quiz was not created for the provided user.")
        
        logging.info(f"📋 Validating responses for User {user_id} on Quiz {quiz_id}")
        submitted_at = time.time()
        # ✅ Find previous attempts correctly
        previous_attempts = responses_collection.count_documents({"user_id": user_id, "quiz_id": quiz_id})
        attempt_number = 1 if previous_attempts == 0 else previous_attempts + 1  # ✅ Initialize correctly

        logging.info(f"🔁 User {user_id} is submitting attempt {attempt_number} for quiz {quiz_id}.")
        
        correct_count = 0  # Track correct answers
        total_time = 0      # Track total quiz time
        total_questions = len(quiz["questions"])

        response_data = {
            "user_id": user_id,
            "quiz_id": quiz_id,
            "submitted_at": submitted_at,
            "attempt_number": attempt_number,  # ✅ Track attempt number correctly
            "responses": [],
            "summary": {},
        }

        # ✅ Ensure all questions are answered
        expected_questions = {q["question_text"] for q in quiz["questions"]}
        submitted_questions = {r.question_text for r in responses}
        missing_questions = expected_questions - submitted_questions

        # ✅ Instead of rejecting the submission, log missing answers as incorrect
        for missed in missing_questions:
            question = next((q for q in quiz["questions"] if q["question_text"] == missed), None)
            if question:
                responses.append(QuizResponse(
                question_text=missed,
                selected_answer="Not Answered",
                time_taken=0  # Assume no time spent
            ))

            logging.warning(f"⚠ User {user_id} skipped {len(missing_questions)} questions. Logged as incorrect.")

        for response in responses:
            try:
                question_text = response.question_text
                selected_answer = response.selected_answer
                time_taken = response.time_taken

                question = next((q for q in quiz["questions"] if q["question_text"] == question_text), None)
                if not question:
                    raise HTTPException(status_code=404, detail=f"Question '{question_text}' not found in the quiz.")

                is_correct = selected_answer == question["correct_answer"]
                if is_correct:
                    correct_count += 1
                total_time += time_taken
                
                response_data["responses"].append({
                    "question_text": question_text,
                    "selected_answer": selected_answer,
                    "correct_answer": question["correct_answer"],
                    "is_correct": is_correct,
                    "time_taken": time_taken,
                    "difficulty": question["difficulty"],
                    "options": {
                        "A": question.get("option1", ""),
                        "B": question.get("option2", ""),
                        "C": question.get("option3", ""),
                        "D": question.get("option4", ""),
                        "E": question.get("option5", "")
                    }
                })
            except Exception as e:
                logging.error(f"❌ Error processing response {response}: {traceback.format_exc()}")
                raise HTTPException(status_code=500, detail=str(e))
            
        # ✅ Calculate Quiz Summary
        accuracy = round((correct_count / total_questions) * 100, 2)
        avg_time_per_question = round(total_time / total_questions, 2)
        
        response_data["summary"] = {
            "total_questions": total_questions,
            "correct_answers": correct_count,
            "incorrect_answers": total_questions - correct_count,
            "accuracy": accuracy,
            "total_time": total_time,
            "avg_time_per_question": avg_time_per_question
        }
        
        logging.info(f"📤 Storing quiz response in the database...")
        # ✅ Insert response data into database
        inserted_response = responses_collection.insert_one(response_data)

        # ✅ Only update performance on the first attempt
        if attempt_number == 1:
            update_user_performance(user_id, response_data["responses"])
            
        # ✅ Convert ObjectId to string for API response
        response_data["_id"] = str(inserted_response.inserted_id)

        logging.info(f"✅ Quiz submitted: All responses saved for User {user_id}.")
        logging.info(f"✅ Returning quiz results: {response_data}")
        return response_data

    except Exception as e:
        logging.error(f"🔥 Error submitting quiz: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/user_performance_chart/{user_id}")
def generate_performance_chart(user_id: str):
    """Generates a performance graph of user progress."""
    user_data = users_collection.find_one({"_id": user_id})
    if not user_data or "history" not in user_data["performance"]:
        raise HTTPException(status_code=404, detail="No performance data found for this user.")

    quiz_numbers = list(range(1, len(user_data["performance"]["history"]) + 1))
    scores = [
    round(sum([q["is_correct"] for q in quiz]) / max(1, len(quiz)) * 100, 2) 
    for quiz in user_data["performance"]["history"] if quiz]

    plt.figure(figsize=(8, 4))
    plt.plot(quiz_numbers, scores, marker="o", linestyle="-", color="b")
    plt.xlabel("Quiz Attempt")
    plt.ylabel("Score (%)")
    plt.title("User Performance Over Time")

    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode()

# ✅ New API Route to Fetch User Quiz History
@router.get("/user_quiz_history/{user_id}")
def get_user_quiz_history(user_id: str,current_user: str = Depends(get_current_user)):
    """
    Retrieve all quizzes a user has attempted along with each attempt.
    """
    try:
        # Step 1: Ensure the user exists
        existing_user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found.")
        
        if current_user != user_id:
            logging.error(f"🚫 Unauthorized access attempt by {current_user}")
            raise HTTPException(status_code=403, detail="Unauthorized access")
    
        # Step 2: Fetch all quiz attempts made by the user
        quiz_attempts = list(responses_collection.find({"user_id": user_id}))

        if not quiz_attempts:
            return {"message": "No quiz attempts found."}

        # Step 3: Structure the quiz history data correctly
        quiz_history = {}
        for attempt in quiz_attempts:
            quiz_id = attempt["quiz_id"]
            if quiz_id not in quiz_history:
                quiz_history[quiz_id] = {
                    "quiz_id": quiz_id,
                    "attempts": []
                }
            
            quiz_history[quiz_id]["attempts"].append({
                "response_id": str(attempt["_id"]),  # ✅ Convert MongoDB _id to string
                "submitted_at": attempt["submitted_at"],
                "attempt_number": attempt["attempt_number"],
                "summary": attempt["summary"]
            })

        return {"quiz_history": list(quiz_history.values())}

    except Exception as e:
        logging.error(f"🔥 Error fetching quiz history: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving quiz history.")

# ✅ New API Route to Fetch Attempt Results
@router.get("/quiz_attempt_results/{user_id}/{quiz_id}/{attempt_number}")
def get_quiz_attempt_results(user_id: str, quiz_id: str, attempt_number: int,current_user: str = Depends(get_current_user)):
    """
    Retrieve a specific quiz attempt's results, including full question details from quizzes_collection.
    """
    try:
        existing_user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not existing_user:
            logging.error(f"❌ User {user_id} not found in the database.")
            raise HTTPException(status_code=404, detail="User not found. Please register before generating a quiz.")
        
        if current_user != user_id:
            logging.error(f"🚫 Unauthorized access attempt by {current_user}")
            raise HTTPException(status_code=403, detail="Unauthorized access")
    
        # Step 1: Retrieve the attempt from responses_collection
        attempt = responses_collection.find_one({
            "user_id": user_id,
            "quiz_id": quiz_id,
            "attempt_number": attempt_number
        })

        if not attempt:
            raise HTTPException(status_code=404, detail="Attempt not found.")

        # Step 2: Retrieve the full quiz details from quizzes_collection
        quiz = quizzes_collection.find_one({"quiz_id": quiz_id})

        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found.")

        # Step 3: Create a dictionary mapping question_text -> full question details
        question_lookup = {q["question_text"]: q for q in quiz["questions"]}

        # Step 4: Merge full question details into attempt responses
        enriched_responses = []
        for response in attempt["responses"]:
            question_text = response["question_text"]

            if question_text in question_lookup:
                full_question = question_lookup[question_text]
                response["options"] = {
                    "A": full_question.get("option1", ""),
                    "B": full_question.get("option2", ""),
                    "C": full_question.get("option3", ""),
                    "D": full_question.get("option4", ""),
                    "E": full_question.get("option5", "")
                }
                response["difficulty"] = full_question["difficulty"]
                response["correct_answer"] = full_question["correct_answer"]

            enriched_responses.append(response)

        # Step 5: Update attempt data with enriched responses
        attempt["responses"] = enriched_responses
        attempt["_id"] = str(attempt["_id"])  # Convert ObjectId to string

        return attempt

    except Exception as e:
        logging.error(f"🔥 Error fetching attempt results: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving attempt results.")
