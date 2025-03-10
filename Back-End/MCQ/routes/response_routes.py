import time
import logging
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from fastapi import APIRouter, HTTPException
from database.database import responses_collection, quizzes_collection, users_collection
from bson import ObjectId
from pydantic import BaseModel
from typing import List
from pymongo.errors import PyMongoError

router = APIRouter()

# Logging Configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# 🔥 Pydantic Model for Each Response
class QuizResponse(BaseModel):
    question_text: str
    selected_answer: str
    time_taken: int  # ✅ Change this to an integer (was previously str)

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
        "easy_correct": 0, "easy_total": 0, "easy_time": 0, "easy_incorrect": 0,
        "medium_correct": 0, "medium_total": 0, "medium_time": 0, "medium_incorrect": 0,
        "hard_correct": 0, "hard_total": 0, "hard_time": 0, "hard_incorrect": 0,
        "history": []
    })

    for response in responses:
        difficulty = response["difficulty"]
        is_correct = response["is_correct"]
        time_taken = response["time_taken"]

        performance[f"{difficulty}_total"] += 1
        if is_correct:
            performance[f"{difficulty}_correct"] += 1
        else:
            performance[f"{difficulty}_incorrect"] += 1  # ✅ Track incorrect responses
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
def submit_quiz(data: SubmitQuizRequest):
    """
    API to store user's quiz responses in MongoDB and update their performance dynamically.
    """
    try:
        user_id = data.user_id
        quiz_id = data.quiz_id
        responses = data.responses  

        existing_user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found. Please register before generating a quiz.")

        # Fetch quiz to validate responses
        quiz = quizzes_collection.find_one({"quiz_id": quiz_id})
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found.")
        
        # ✅ Check that the quiz was created for this user
        if str(quiz.get("user_id")) != str(user_id):
            raise HTTPException(status_code=403, detail="This quiz was not created for the provided user.")
        
        # ✅ Check if this quiz was already submitted
        previous_submission = responses_collection.find_one({"user_id": user_id, "quiz_id": quiz_id})

        is_first_attempt = previous_submission is None  # True if first attempt, False if repeat
        
        submitted_at = time.time()

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
            
        # ✅ Prepare response document
        response_data = {
            "user_id": user_id,
            "quiz_id": quiz_id,
            "submitted_at": submitted_at,
            "responses": [],
            "is_first_attempt": is_first_attempt  # ✅ Track first attempts
        }

        seen_questions = set()  # Track seen questions

        for response in responses:
            question_text = response.question_text
            selected_answer = response.selected_answer
            time_taken = response.time_taken

            # Find the correct question
            question = next((q for q in quiz["questions"] if q["question_text"] == question_text), None)
            if not question:
                raise HTTPException(status_code=404, detail=f"Question '{question_text}' not found in the quiz.")

            is_correct = selected_answer == question["correct_answer"]

            response_data["responses"].append({
                "question_text": question_text,
                "selected_answer": selected_answer,
                "correct_answer": question["correct_answer"],
                "is_correct": is_correct,
                "time_taken": time_taken,
                "difficulty": question["difficulty"]
            })

            # Store seen questions
            seen_questions.add(question_text)

        # ✅ Insert response data into database
        inserted_response = responses_collection.insert_one(response_data)

        # ✅ Only update performance on the first attempt
        if is_first_attempt:
            update_user_performance(user_id, response_data["responses"])
            
        # ✅ Convert ObjectId to string for API response
        response_data["_id"] = str(inserted_response.inserted_id)

        logging.info(f"✅ Quiz submitted: All responses saved for User {user_id}.")

        return {
            "message": "Quiz submitted successfully",
            "user_id": user_id,
            "quiz_id": quiz_id,
            "submitted_at": submitted_at,
            "responses": response_data["responses"]
        }

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

@router.get("/quiz_attempts/{user_id}/{quiz_id}")
def get_quiz_attempts(user_id: str, quiz_id: str):
    """
    Retrieve all attempts for a specific quiz by a user.
    """
    try:
        existing_user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found.")

        quiz_attempts = list(responses_collection.find({"user_id": user_id, "quiz_id": quiz_id}))

        if not quiz_attempts:
            raise HTTPException(status_code=404, detail="No attempts found for this quiz.")

        return {
            "quiz_id": quiz_id,
            "attempts": [
                {
                    "attempt_id": str(attempt["_id"]),
                    "submitted_at": attempt["submitted_at"],
                    "is_first_attempt": attempt["is_first_attempt"],
                    "responses": attempt["responses"]
                }
                for attempt in quiz_attempts
            ]
        }

    except Exception as e:
        logging.error(f"🔥 Error fetching quiz attempts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

