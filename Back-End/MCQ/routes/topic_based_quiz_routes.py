from fastapi import APIRouter, HTTPException, Depends
from pymongo import MongoClient
from bson import ObjectId, errors
from pydantic import BaseModel
from datetime import datetime  # ✅ Correct import
import logging
from database.database import topic_quizzes, topic_quiz_attempts
from bson.errors import InvalidId

router = APIRouter()
# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Pydantic model for request validation
class Question(BaseModel):
    question_text: str
    option1: str
    option2: str
    option3: str
    option4: str
    option5: str
    correct_answer: str

class QuizRequest(BaseModel):
    topic_name: str
    questions: list[Question]
    
class ResponseItem(BaseModel):
    question_text: str
    selected_answer: str

class QuizSubmission(BaseModel):
    user_id: str
    quiz_id: str
    responses: list[ResponseItem]

@router.post("/topic_quiz/create")
def create_topic_quiz(quiz_data: QuizRequest):
    """Creates a new topic-wise quiz with 30 MCQs, each having 5 options and a correct answer."""
    
    if len(quiz_data.questions) != 30:
        logging.error("❌ Quiz creation failed: Invalid question count")
        raise HTTPException(status_code=400, detail="A quiz must contain exactly 30 questions.")

    # Convert to proper structure
    formatted_questions = [
        {
            "question_text": q.question_text,
            "options": {
                "A": q.option1,
                "B": q.option2,
                "C": q.option3,
                "D": q.option4,
                "E": q.option5
            },
            "correct_answer": q.correct_answer
        }
        for q in quiz_data.questions
    ]

    quiz_entry = {
        "topic_name": quiz_data.topic_name,
        "questions": formatted_questions,
        "created_at": datetime.datetime.utcnow()
    }
    
    quiz_id = topic_quizzes.insert_one(quiz_entry).inserted_id
    return {"message": "Quiz created successfully!", "quiz_id": str(quiz_id)}


@router.get("/topic_quiz/all")
def get_all_topic_quizzes():
    """Fetches all available topic-wise quizzes."""
    quizzes = list(topic_quizzes.find({}, {"_id": 1, "topic_name": 1}))
    return [{"quiz_id": str(q["_id"]), "topic_name": q["topic_name"]} for q in quizzes]


@router.get("/topic_quiz/{quiz_id}")
def get_topic_quiz(quiz_id: str):
    try:
        # Validate and convert quiz_id to ObjectId
        quiz_obj_id = ObjectId(quiz_id)
    except errors.InvalidId:
        logging.error(f"❌ Invalid quiz_id: {quiz_id}")
        raise HTTPException(status_code=400, detail="Invalid quiz_id format.")

    # Query the quiz
    quiz = topic_quizzes.find_one({"_id": quiz_obj_id}, {"_id": 1, "topic_name": 1, "questions": 1})

    if not quiz:
        logging.error(f"❌ Quiz not found for ID: {quiz_id}")
        raise HTTPException(status_code=404, detail="Quiz not found.")

    # ✅ Convert ObjectId to string before returning
    quiz["_id"] = str(quiz["_id"])

    return quiz

# User submits quiz answers, which are stored and marked as completed.

@router.post("/questions/submit")
def submit_topic_quiz(submission: QuizSubmission):
    """User submits quiz answers, which are stored and marked as completed."""

    user_id = submission.user_id
    quiz_id = submission.quiz_id
    responses = submission.responses

    # ✅ Ensure quiz exists
    try:
        quiz = topic_quizzes.find_one({"_id": ObjectId(quiz_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid quiz ID format.")

    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found.")

    # ✅ Ensure user hasn't completed this quiz already
    existing_attempt = topic_quiz_attempts.find_one({"quiz_id": quiz_id, "user_id": user_id})
    if existing_attempt:
        raise HTTPException(status_code=403, detail="Quiz already completed.")

    # ✅ Process user responses
    correct_answers = {q["question_text"]: q["correct_answer"] for q in quiz["questions"]}
    
    score = 0
    graded_responses = []
    
    for response in responses:
        question_text = response.question_text
        selected_answer = response.selected_answer
        is_correct = selected_answer == correct_answers.get(question_text)
        
        graded_responses.append({
            "question_text": question_text,
            "selected_answer": selected_answer,
            "correct_answer": correct_answers.get(question_text),
            "is_correct": is_correct
        })
        
        if is_correct:
            score += 1

    # ✅ Store attempt
    attempt_data = {
        "user_id": user_id,
        "quiz_id": quiz_id,
        "submitted_at": datetime.utcnow(),
        "responses": graded_responses,
        "score": score,
        "completed": True
    }
    attempt_id = topic_quiz_attempts.insert_one(attempt_data).inserted_id

    return {
        "message": "Quiz submitted successfully!",
        "attempt_id": str(attempt_id),
        "score": score
    }

@router.get("/quiz_topic/results/{quiz_id}")
def get_topic_quiz_results(user_id: str, quiz_id: str):
    """Fetches a user's results for a completed topic quiz with full question data."""
    
    # Find the user's attempt
    attempt = topic_quiz_attempts.find_one({"quiz_id": quiz_id, "user_id": user_id})
    
    if not attempt:
        raise HTTPException(status_code=404, detail="No results found for this quiz.")

    # Find the original quiz to retrieve full question details
    quiz = topic_quizzes.find_one({"_id": ObjectId(quiz_id)}, {"questions": 1})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found.")

    # Create a detailed result structure
    detailed_results = []

    # Convert questions into a dictionary for easy lookup
    question_lookup = {q["question_text"]: q for q in quiz["questions"]}

    for response in attempt["responses"]:
        question_text = response["question_text"]
        selected_answer = response["selected_answer"]
        correct_answer = response["correct_answer"]
        is_correct = response["is_correct"]

        # Retrieve original question details
        question_details = question_lookup.get(question_text, {})
        
        detailed_results.append({
            "question_text": question_text,
            "options": question_details.get("options", {}),
            "selected_answer": selected_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct
        })

    return {
        "quiz_id": quiz_id,
        "user_id": user_id,
        "submitted_at": attempt["submitted_at"],
        "score": attempt["score"],
        "responses": detailed_results
    }
    
@router.get("/quiz/completed/{user_id}")
def get_completed_topic_quizzes(user_id: str):
    """Fetches all topic quizzes that a user has completed."""
    
    if not user_id:
        logging.error("❌ Invalid Request: user_id is missing")
        raise HTTPException(status_code=400, detail="User ID is required.")

    # Find all quiz attempts by the user
    completed_attempts = list(topic_quiz_attempts.find(
        {"user_id": user_id}, 
        {"_id": 0, "quiz_id": 1}
    ))

    if not completed_attempts:
        logging.info(f"✅ No completed quizzes found for user: {user_id}")
        return {"completed_quizzes": []}

    # Extract and validate quiz IDs
    completed_quizzes = []
    for attempt in completed_attempts:
        quiz_id = attempt.get("quiz_id")
        if quiz_id and isinstance(quiz_id, str):  # Ensure it's a valid string
            completed_quizzes.append(quiz_id)
        else:
            logging.error(f"❌ Invalid quiz_id found: {quiz_id}")

    return {"completed_quizzes": completed_quizzes}

