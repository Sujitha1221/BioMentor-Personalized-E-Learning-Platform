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
from utils.verification import verify_mcq_with_llm
from datetime import datetime, timedelta

router = APIRouter()

# Logging Configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


#  Pydantic Model for Each Response
class QuizResponse(BaseModel):
    question_text: str
    selected_answer: str
    time_taken: float  #  Change this to an integer (was previously str)


#  Pydantic Model for Submitting Quiz
class SubmitQuizRequest(BaseModel):
    user_id: str
    quiz_id: str
    responses: List[QuizResponse]  #  Expect a list of QuizResponse objects

# Function to Estimate Student Ability
def estimate_student_ability(user_id):
    """Estimates student ability dynamically using accuracy & response time from the last 10 quizzes."""
    user_data = users_collection.find_one({"_id": ObjectId(user_id)})

    if (
        not user_data
        or "performance" not in user_data
        or "last_10_quizzes" not in user_data["performance"]
    ):
        logging.error(
            f" No performance data found for user {user_id}. Returning default ability."
        )
        return 0  # Default ability score

    responses = user_data["performance"]["last_10_quizzes"]
    # logging.info(f"📥 Raw responses for user {user_id}: {responses}")

    if not isinstance(responses, list):
        logging.error(
            f" Expected list for responses but got {type(responses)}: {responses}"
        )
        return 0

    if not responses:
        return 0  # No quizzes taken

    #  Compute Average Accuracy Across Last 10 Quizzes
    total_accuracy = sum(quiz.get("accuracy", 0) for quiz in responses)
    avg_accuracy = total_accuracy / len(responses) if responses else 0

    #  Compute Weighted Average Time
    total_time = sum(quiz.get("total_time", 0) for quiz in responses)
    avg_time = total_time / len(responses) if responses else 0

    #  Adjust Time-Based Penalty Dynamically
    if avg_time < 3:
        time_penalty = 0.3  # 🚨 Very fast responses (possible guessing)
    elif 3 <= avg_time < 7:
        time_penalty = 0.2  # ⚠ Slightly too fast
    elif 7 <= avg_time < 90:
        time_penalty = 0.0  #  Normal thoughtful response
    elif 90 <= avg_time < 120:
        time_penalty = 0.1  # 🕒 Slightly long
    else:
        time_penalty = 0.2  # ⏳ Very long (possible distractions)

    #  Apply Ability Estimation Formula
    ability = np.log(avg_accuracy / max(1, (100 - avg_accuracy + 1))) - time_penalty

    return round(ability, 2)

# Function to Update User Performance
def update_user_performance(user_id, responses):
    """Updates the user's accuracy and response time for each difficulty level."""
    user_data = users_collection.find_one({"_id": ObjectId(user_id)})

    if not user_data:
        logging.error(f" User {user_id} not found. Aborting update.")
        raise ValueError(f"User {user_id} not found in the database.")

    performance = user_data.get(
        "performance",
        {
            "total_quizzes": 0,
            "accuracy_easy": 0,
            "accuracy_medium": 0,
            "accuracy_hard": 0,
            "time_easy": 0,
            "time_medium": 0,
            "time_hard": 0,
            "strongest_area": None,
            "weakest_area": None,
            "last_10_quizzes": [],
            "consistency_score": 0,
        },
    )

    correct_answers = {"easy": 0, "medium": 0, "hard": 0}
    total_questions = {"easy": 0, "medium": 0, "hard": 0}
    time_spent = {"easy": 0, "medium": 0, "hard": 0}

    for response in responses:
        difficulty = response["difficulty"]
        is_correct = response["is_correct"]
        time_taken = response["time_taken"]

        total_questions[difficulty] += 1
        if is_correct:
            correct_answers[difficulty] += 1
        time_spent[difficulty] += time_taken

    # Update Accuracy and Time Data
    for difficulty in ["easy", "medium", "hard"]:
        if total_questions[difficulty] > 0:
            accuracy = (correct_answers[difficulty] / total_questions[difficulty]) * 100
            performance[f"accuracy_{difficulty}"] = round(accuracy, 2)
            performance[f"time_{difficulty}"] += time_spent[difficulty]

    # Track Last 10 Quiz Performance
    quiz_performance = {
        "accuracy": round(
            (sum(correct_answers.values()) / sum(total_questions.values())) * 100, 2
        ),
        "total_time": sum(time_spent.values()),
        "timestamp": time.time(),
    }
    performance["last_10_quizzes"].append(quiz_performance)
    if len(performance["last_10_quizzes"]) > 10:
        performance["last_10_quizzes"].pop(0)

    # Calculate Strongest and Weakest Area
    difficulties = ["easy", "medium", "hard"]
    strongest = max(difficulties, key=lambda d: performance[f"accuracy_{d}"])
    weakest = min(difficulties, key=lambda d: performance[f"accuracy_{d}"])

    performance["strongest_area"] = strongest
    performance["weakest_area"] = weakest

    # Calculate Consistency Score (How Often User Takes Quizzes)
    last_10_timestamps = [q["timestamp"] for q in performance["last_10_quizzes"]]
    if len(last_10_timestamps) >= 2:
        avg_time_gap = sum(
            last_10_timestamps[i] - last_10_timestamps[i - 1]
            for i in range(1, len(last_10_timestamps))
        ) / (len(last_10_timestamps) - 1)
        performance["consistency_score"] = max(
            100 - avg_time_gap // 86400, 0
        )  # Normalize Score (0-100)

    # Increment Total Quizzes Count
    performance["total_quizzes"] += 1
    try:
        result = users_collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": {"performance": performance}}
        )

        if result.matched_count == 0:
            logging.error(
                f"No matching user found for ID {user_id}. Performance update failed."
            )
            raise ValueError(
                f"Failed to update performance: No matching user found for ID {user_id}."
            )

        if result.modified_count == 0:
            logging.warning(
                f"⚠ Performance data for User {user_id} was not modified. Possible no changes."
            )

        logging.info(f" User performance updated successfully for User {user_id}.")

    except PyMongoError as e:
        logging.error(f" MongoDB Error updating user performance: {e}")
        raise RuntimeError(f"Database error while updating user performance: {e}")

# API Route to Submit Quiz
@router.post("/submit_quiz/")
def submit_quiz(data: SubmitQuizRequest, current_user: str = Depends(get_current_user)):
    """
    API to store user's quiz responses in MongoDB and update their performance dynamically.
    """
    try:
        user_id = data.user_id
        quiz_id = data.quiz_id
        responses = data.responses

        logging.info(
            f"Received quiz submission: User {user_id}, Quiz {quiz_id}, Responses Count: {len(responses)}"
        )

        existing_user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not existing_user:
            logging.error(f" User {user_id} not found in the database.")
            raise HTTPException(
                status_code=404,
                detail="User not found. Please register before generating a quiz.",
            )

        if current_user != user_id:
            logging.error(f" Unauthorized access attempt by {current_user}")
            raise HTTPException(status_code=403, detail="Unauthorized access")

        # Fetch quiz to validate responses
        quiz = quizzes_collection.find_one({"quiz_id": quiz_id})
        if not quiz:
            logging.error(f" Quiz {quiz_id} not found in the database.")
            raise HTTPException(status_code=404, detail="Quiz not found.")

        #  Check that the quiz was created for this user
        if str(quiz.get("user_id")) != str(user_id):
            raise HTTPException(
                status_code=403,
                detail="This quiz was not created for the provided user.",
            )

        logging.info(f"Validating responses for User {user_id} on Quiz {quiz_id}")
        submitted_at = time.time()
        #  Find previous attempts correctly
        previous_attempts = responses_collection.count_documents(
            {"user_id": user_id, "quiz_id": quiz_id}
        )
        attempt_number = (
            1 if previous_attempts == 0 else previous_attempts + 1
        )  #  Initialize correctly

        MAX_ATTEMPTS = 3
        if previous_attempts >= MAX_ATTEMPTS:
            logging.warning(
                f"❌ User {user_id} has reached the maximum number of attempts for quiz {quiz_id}."
            )
            raise HTTPException(
                status_code=403,
                detail="You have reached the maximum number of attempts for this quiz.",
            )

        logging.info(
            f"User {user_id} is submitting attempt {attempt_number} for quiz {quiz_id}."
        )

        correct_count = 0  # Track correct answers
        total_time = 0  # Track total quiz time
        total_questions = len(quiz["questions"])

        response_data = {
            "user_id": user_id,
            "quiz_id": quiz_id,
            "submitted_at": submitted_at,
            "attempt_number": attempt_number,  #  Track attempt number correctly
            "responses": [],
            "summary": {},
        }

        #  Ensure all questions are answered
        expected_questions = {q["question_text"] for q in quiz["questions"]}
        submitted_questions = {r.question_text for r in responses}
        missing_questions = expected_questions - submitted_questions

        #  Instead of rejecting the submission, log missing answers as incorrect
        for missed in missing_questions:
            question = next(
                (q for q in quiz["questions"] if q["question_text"] == missed), None
            )
            if question:
                responses.append(
                    QuizResponse(
                        question_text=missed,
                        selected_answer="Not Answered",
                        time_taken=0,  # Assume no time spent
                    )
                )

            logging.warning(
                f"⚠ User {user_id} skipped {len(missing_questions)} questions. Logged as incorrect."
            )

        for response in responses:
            try:
                question_text = response.question_text
                selected_answer = response.selected_answer
                time_taken = response.time_taken

                question = next(
                    (
                        q
                        for q in quiz["questions"]
                        if q["question_text"] == question_text
                    ),
                    None,
                )
                if not question:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Question '{question_text}' not found in the quiz.",
                    )

                if not question.get("is_verified", False):
                    logging.info(
                        f"🔍 Re-verifying unverified question during submission: {question_text[:60]}..."
                    )

                    options = {
                        "A": question.get("option1", ""),
                        "B": question.get("option2", ""),
                        "C": question.get("option3", ""),
                        "D": question.get("option4", ""),
                        "E": question.get("option5", ""),
                    }

                    claimed_answer = question.get("correct_answer", "N/A")
                    is_correct_late, verified, claimed = verify_mcq_with_llm(
                        question_text, options, claimed_answer
                    )

                    question["claimed_answer"] = (
                        claimed  # ✅ Store model's original answer
                    )

                    if is_correct_late is False and verified in options:
                        logging.warning(f"✅ Late fix: {claimed} → {verified}")
                        question["correct_answer"] = verified
                        question["verified_answer"] = verified
                    elif is_correct_late is True:
                        question["correct_answer"] = claimed
                        question["verified_answer"] = claimed
                    else:
                        question["correct_answer"] = claimed
                        question["verified_answer"] = None

                    question["is_verified"] = True

                is_correct = selected_answer == question.get(
                    "verified_answer", question["correct_answer"]
                )
                if is_correct:
                    correct_count += 1
                total_time += time_taken

                response_data["responses"].append(
                    {
                        "question_text": question_text,
                        "selected_answer": selected_answer,
                        "claimed_answer": question.get(
                            "claimed_answer", question.get("correct_answer")
                        ),
                        "verified_answer": question.get(
                            "verified_answer", question["correct_answer"]
                        ),
                        "correct_answer": question.get(
                            "verified_answer", question["correct_answer"]
                        ),
                        "is_correct": selected_answer
                        == question.get("verified_answer", question["correct_answer"]),
                        "time_taken": time_taken,
                        "difficulty": question["difficulty"],
                        "options": {
                            "A": question.get("option1", ""),
                            "B": question.get("option2", ""),
                            "C": question.get("option3", ""),
                            "D": question.get("option4", ""),
                            "E": question.get("option5", ""),
                        },
                    }
                )

            except Exception as e:
                logging.error(
                    f" Error processing response {response}: {traceback.format_exc()}"
                )
                raise HTTPException(status_code=500, detail=str(e))

        #  Calculate Quiz Summary
        accuracy = round((correct_count / total_questions) * 100, 2)
        avg_time_per_question = round(total_time / total_questions, 2)

        response_data["summary"] = {
            "total_questions": total_questions,
            "correct_answers": correct_count,
            "incorrect_answers": total_questions - correct_count,
            "accuracy": accuracy,
            "total_time": total_time,
            "avg_time_per_question": avg_time_per_question,
        }

        logging.info(f"📤 Storing quiz response in the database...")
        #  Insert response data into database
        inserted_response = responses_collection.insert_one(response_data)

        #  Only update performance on the first attempt
        if attempt_number == 1:
            update_user_performance(user_id, response_data["responses"])

        #  Convert ObjectId to string for API response
        response_data["_id"] = str(inserted_response.inserted_id)

        logging.info(f" Quiz submitted: All responses saved for User {user_id}.")
        logging.info(f" Returning quiz results: {response_data}")
        return response_data

    except Exception as e:
        logging.error(f" Error submitting quiz: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


#  New API Route to Fetch User Quiz History
@router.get("/user_quiz_history/{user_id}")
def get_user_quiz_history(user_id: str, current_user: str = Depends(get_current_user)):
    """
    Retrieve all quizzes a user has attempted along with each attempt.
    """
    try:
        # Step 1: Ensure the user exists
        existing_user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found.")

        if current_user != user_id:
            logging.error(f" Unauthorized access attempt by {current_user}")
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
                quiz_history[quiz_id] = {"quiz_id": quiz_id, "attempts": []}

            quiz_history[quiz_id]["attempts"].append(
                {
                    "response_id": str(
                        attempt["_id"]
                    ),  #  Convert MongoDB _id to string
                    "submitted_at": attempt["submitted_at"],
                    "attempt_number": attempt["attempt_number"],
                    "summary": attempt["summary"],
                }
            )

        return {"quiz_history": list(quiz_history.values())}

    except Exception as e:
        logging.error(f" Error fetching quiz history: {str(e)}")
        raise HTTPException(
            status_code=500, detail="An error occurred while retrieving quiz history."
        )

#  New API Route to Fetch Attempt Results
@router.get("/quiz_attempt_results/{user_id}/{quiz_id}/{attempt_number}")
def get_quiz_attempt_results(
    user_id: str,
    quiz_id: str,
    attempt_number: int,
    current_user: str = Depends(get_current_user),
):
    """
    Retrieve a specific quiz attempt's results, including full question details from quizzes_collection.
    """
    try:
        existing_user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not existing_user:
            logging.error(f" User {user_id} not found in the database.")
            raise HTTPException(
                status_code=404,
                detail="User not found. Please register before generating a quiz.",
            )

        if current_user != user_id:
            logging.error(f" Unauthorized access attempt by {current_user}")
            raise HTTPException(status_code=403, detail="Unauthorized access")

        # Step 1: Retrieve the attempt from responses_collection
        attempt = responses_collection.find_one(
            {"user_id": user_id, "quiz_id": quiz_id, "attempt_number": attempt_number}
        )

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
                    "E": full_question.get("option5", ""),
                }
                response["difficulty"] = full_question["difficulty"]
                response["claimed_answer"] = full_question.get(
                    "claimed_answer", full_question.get("correct_answer")
                )
                response["verified_answer"] = full_question.get(
                    "verified_answer", full_question["correct_answer"]
                )
                response["correct_answer"] = response[
                    "verified_answer"
                ]  # for consistency

            enriched_responses.append(response)

        # Step 5: Update attempt data with enriched responses
        attempt["responses"] = enriched_responses
        attempt["_id"] = str(attempt["_id"])  # Convert ObjectId to string

        return attempt

    except Exception as e:
        logging.error(f" Error fetching attempt results: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while retrieving attempt results.",
        )

# API Route to Generate Performance Graph
@router.get("/performance_graph/{user_id}")
def generate_performance_graph(
    user_id: str, current_user: str = Depends(get_current_user)
):
    """Generates graphs showing user improvement and consistency."""
    user_data = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found.")

    if current_user != user_id:
        logging.error(f" Unauthorized access attempt by {current_user}")
        raise HTTPException(status_code=403, detail="Unauthorized access")

    if (
        not user_data
        or "performance" not in user_data
        or "last_10_quizzes" not in user_data["performance"]
    ):
        return {
            "quiz_numbers": [],
            "scores": [],
            "graph_image": None,
            "message": "No quiz performance data available. Start taking quizzes to see your progress!",
        }
    history = user_data["performance"]["last_10_quizzes"]

    quiz_numbers = list(range(1, len(history) + 1))
    scores = [quiz["accuracy"] for quiz in history]

    plt.figure(figsize=(8, 4))
    plt.plot(
        quiz_numbers, scores, marker="o", linestyle="-", color="b", label="Accuracy (%)"
    )
    plt.xlabel("Quiz Attempt")
    plt.ylabel("Score (%)")
    plt.title("User Performance Over Time")
    plt.legend()

    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    return {
        "quiz_numbers": quiz_numbers,
        "scores": scores,
        "graph_image": base64.b64encode(img.getvalue()).decode(),
        "message": "Performance data loaded successfully.",
    }

# API Route to Fetch Progress Insights
@router.get("/progress_insights/{user_id}")
def get_progress_insights(user_id: str, current_user: str = Depends(get_current_user)):
    """Analyzes user progress and provides AI-driven insights."""
    user_data = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found.")

    if not user_data or "performance" not in user_data:
        raise HTTPException(status_code=404, detail="No performance data found.")

    if current_user != user_id:
        logging.error(f" Unauthorized access attempt by {current_user}")
        raise HTTPException(status_code=403, detail="Unauthorized access")

    history = user_data["performance"].get("last_10_quizzes", [])

    if len(history) == 0:
        return {
            "message": "No quiz attempts found. Start taking quizzes to track your progress!"
        }

    if len(history) == 1:
        #  User has only one attempt – give insights based on it
        first_attempt = history[0]
        return {
            "accuracy_trend": [first_attempt["accuracy"]],
            "time_trend": [first_attempt["total_time"]],
            "accuracy_improvement": 0,
            "time_efficiency": 0,
            "suggestion": "You’ve completed your first quiz! Keep practicing to track your progress over time.",
        }

    #  User has multiple attempts – calculate progress trends
    accuracy_trend = [quiz["accuracy"] for quiz in history]
    time_trend = [quiz["total_time"] for quiz in history]

    accuracy_change = round(accuracy_trend[-1] - accuracy_trend[0], 2)
    time_change = round(time_trend[-1] - time_trend[0], 2)

    insights = {
        "accuracy_trend": accuracy_trend,
        "time_trend": time_trend,
        "accuracy_improvement": accuracy_change,
        "time_efficiency": time_change,
        "suggestion": "",
    }

    #  AI-Driven Suggestions
    if accuracy_change > 5:
        insights["suggestion"] = (
            "Great job! Your accuracy is improving steadily. Keep practicing!"
        )
    elif accuracy_change < -5:
        insights["suggestion"] = (
            "Your accuracy has dropped. Try revising incorrect answers."
        )
    else:
        insights["suggestion"] = "You're maintaining a steady performance. Keep going!"

    return insights

# API Route to Compare User Performance
@router.get("/user_performance_comparison/{user_id}")
def get_user_performance_comparison(
    user_id: str, current_user: str = Depends(get_current_user)
):
    """Compares user's performance against average stats of all users."""
    user_data = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found.")
    
    if current_user != user_id:
        logging.error(f" Unauthorized access attempt by {current_user}")
        raise HTTPException(status_code=403, detail="Unauthorized access")
    
    if "performance" not in user_data:
        raise HTTPException(status_code=404, detail="No performance data found.")
    
    last_quizzes = user_data["performance"].get("last_10_quizzes", [])
    if not last_quizzes:
        return {"message": "Not enough data for comparison."}

    all_users = users_collection.find({"performance.total_quizzes": {"$gt": 0}})
    
    total_accuracy = []
    total_time = []

    for user in all_users:
        performance = user.get("performance", {})
        user_last_quizzes = performance.get("last_10_quizzes", [])
        if user_last_quizzes:
            total_accuracy.append(user_last_quizzes[-1]["accuracy"])
            total_time.append(user_last_quizzes[-1]["total_time"])

    if not total_accuracy:
        return {"message": "Not enough data for comparison."}

    user_accuracy = last_quizzes[-1]["accuracy"]
    user_time = last_quizzes[-1]["total_time"]

    avg_accuracy = sum(total_accuracy) / len(total_accuracy)
    avg_time = sum(total_time) / len(total_time)

    return {
        "user_accuracy": user_accuracy,
        "average_accuracy": round(avg_accuracy, 2),
        "user_time": user_time,
        "average_time": round(avg_time, 2),
        "comparison_accuracy": "Higher" if user_accuracy > avg_accuracy else "Lower",
        "comparison_time": "Faster" if user_time < avg_time else "Slower",
    }


@router.get("/engagement_score/{user_id}")
def get_engagement_score(user_id: str, current_user: str = Depends(get_current_user)):
    """Calculates how active and engaged the user is."""
    user_data = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found.")
    if current_user != user_id:
        logging.error(f" Unauthorized access attempt by {current_user}")
        raise HTTPException(status_code=403, detail="Unauthorized access")

    if not user_data or "performance" not in user_data:
        raise HTTPException(status_code=404, detail="No performance data found.")

    history = user_data["performance"].get("last_10_quizzes", [])

    #  Handling Users with Only 1 or 2 Quiz Attempts
    if len(history) == 1:
        return {
            "engagement_score": "Starter",
            "category": "You're off to a great start! Keep going to build consistency.",
        }

    if len(history) == 2:
        return {
            "engagement_score": "Developing",
            "category": "You're beginning to build a habit. Try to maintain consistency!",
        }

    #  Users with 3+ quizzes: Calculate engagement score normally
    consistency_score = user_data["performance"].get("consistency_score", 0)

    if consistency_score > 80:
        category = "Highly Engaged Learner"
    elif consistency_score > 50:
        category = "Moderately Engaged Learner"
    else:
        category = "Needs Improvement"

    return {"engagement_score": consistency_score, "category": category}

#  API Route to Fetch Dashboard Data
@router.get("/dashboard_data/{user_id}")
def get_dashboard_data(user_id: str, current_user: str = Depends(get_current_user)):
    """Returns structured performance data for the user dashboard."""
    user_data = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found.")

    if current_user != user_id:
        logging.error(f" Unauthorized access attempt by {current_user}")
        raise HTTPException(status_code=403, detail="Unauthorized access")

    #  If user has no performance data, return default values
    if not user_data or "performance" not in user_data:
        return {
            "total_quizzes": 0,
            "accuracy_easy": 0,
            "accuracy_medium": 0,
            "accuracy_hard": 0,
            "time_easy": 0,
            "time_medium": 0,
            "time_hard": 0,
            "strongest_area": "N/A",
            "weakest_area": "N/A",
            "consistency_score": 0,
            "last_10_quizzes": [],
            "message": "No quiz data available yet. Start taking quizzes!",
        }
    performance = user_data["performance"]

    return {
        "total_quizzes": performance.get("total_quizzes", 0),
        "accuracy_easy": performance.get("accuracy_easy", 0),
        "accuracy_medium": performance.get("accuracy_medium", 0),
        "accuracy_hard": performance.get("accuracy_hard", 0),
        "time_easy": performance.get("time_easy", 0),
        "time_medium": performance.get("time_medium", 0),
        "time_hard": performance.get("time_hard", 0),
        "strongest_area": performance.get("strongest_area", "N/A"),
        "weakest_area": performance.get("weakest_area", "N/A"),
        "consistency_score": performance.get("consistency_score", 0),
        "last_10_quizzes": performance.get("last_10_quizzes", []),
    }


# Check if the user has any previous quizzes
@router.get("/users/{user_id}/has_previous_quiz")
def check_user_quiz_history(user_id: str):
    """
    Check if the user has any previous quizzes by searching in the `quizzes` collection.
    Returns True if at least one quiz exists.
    """
    try:
        # Ensure the user exists
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            logging.error(f" User not found: {user_id}")
            raise HTTPException(status_code=404, detail="User not found.")

        # Check if the user has any quizzes
        quiz_count = quizzes_collection.count_documents({"user_id": user_id})

        return {"has_previous_quiz": quiz_count > 0}

    except Exception as e:
        logging.error(f" Error checking user quiz history: {str(e)}")
        return HTTPException(status_code=500, detail=str(e))


# API Route to Fetch Leaderboard
@router.get("/leaderboard")
def get_leaderboard():
    """
    Generates a leaderboard of top users based on their latest accuracy.
    """
    try:
        users = users_collection.find(
            {"performance.last_10_quizzes": {"$exists": True, "$ne": []}}
        )

        leaderboard = []
        for user in users:
            quizzes = user.get("performance", {}).get("last_10_quizzes", [])
            if not quizzes:
                continue
            latest_accuracy = quizzes[-1]["accuracy"]
            leaderboard.append(
                {
                    "user_id": str(user["_id"]),
                    "name": user.get(
                        "username", ""
                    ),  # Optional: You can store name/email for display
                    "accuracy": round(latest_accuracy, 2),
                }
            )

        # Sort and return top 10
        leaderboard = sorted(leaderboard, key=lambda x: x["accuracy"], reverse=True)[
            :10
        ]
        return {"leaderboard": leaderboard}

    except Exception as e:
        logging.error(f"Failed to fetch leaderboard: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving leaderboard.")

# API Route to Fetch User Streak
@router.get("/user_streak/{user_id}")
def get_user_streak(user_id: str, current_user: str = Depends(get_current_user)):
    if current_user != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    user_data = users_collection.find_one({"_id": ObjectId(user_id)})

    if not user_data or "performance" not in user_data:
        return {"streak": 0, "longest_streak": 0}

    quizzes = user_data["performance"].get("last_10_quizzes", [])
    if not quizzes:
        return {"streak": 0, "longest_streak": 0}

    # Extract and sort unique quiz dates
    quiz_dates = sorted(
        set(datetime.fromtimestamp(q["timestamp"]).date() for q in quizzes),
        reverse=True
    )

    # Compute current streak
    today = datetime.utcnow().date()
    streak = 0
    for i, date in enumerate(quiz_dates):
        if i == 0:
            if date == today:
                streak += 1
            elif date == today - timedelta(days=1):
                streak += 1
            else:
                break
        else:
            expected = quiz_dates[i - 1] - timedelta(days=1)
            if date == expected:
                streak += 1
            else:
                break

    # Optional: calculate longest streak
    longest_streak = 1
    temp_streak = 1
    for i in range(1, len(quiz_dates)):
        if quiz_dates[i] == quiz_dates[i - 1] - timedelta(days=1):
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            temp_streak = 1

    return {"streak": streak, "longest_streak": longest_streak}
