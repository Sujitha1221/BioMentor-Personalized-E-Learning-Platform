import logging
import requests
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import pandas as pd
from generate_answers import generate_structured_answer, generate_essay_answer
from evaluate_answers import evaluate_user_answer
from answer_evaluation_tool import get_student_analytic_details, convert_objectid,  generate_mind_map
from exam_practice import get_questions_by_student_id, compare_with_passpaper_answer
from predict_question_acceptability import moderate_question
from check_user_availability import check_user_availability
from fastapi.middleware.cors import CORSMiddleware
from duckduckgo_search import DDGS  

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

# Initialize FastAPI app
app = FastAPI()

# Load environment variables from .env file
load_dotenv()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your frontend URL for better security
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Define a generate answer request schema for the API
class QuestionRequest(BaseModel):
    student_id: str
    question: str
    type: str  

# Define a evaluate answer request schema for the API
class EvaluationRequest(BaseModel):
    student_id: str
    question: str
    user_answer: str
    question_type: str 

class StudentEvaluationRequest(BaseModel):
    student_id: str


@app.post("/generate-answer")
def generate_answer(request: QuestionRequest):
    """
    API endpoint to generate an answer based on the question type.
    """
    available, message = check_user_availability(request.student_id)
    if not available:
        raise HTTPException(status_code=404, detail="User not found.")
    
    logging.info(f"Received request to generate answer: {request.dict()}")
    question_type = request.type.lower()  # Normalize type to lowercase

    is_acceptable, moderation_message = moderate_question(request.question)
    if not is_acceptable:
        logging.warning(f"Question moderated: {moderation_message}")
        raise HTTPException(status_code=400, detail=moderation_message)
    
    try:
        if question_type == "structured":
            # Generate a structured answer
            answer = generate_structured_answer(
                query=request.question,
                k=3,  # Default k for structured
                max_words=50  # Default max words for structured
            )

            related_websites = get_related_websites(request.question)
            logging.info("Structured answer generated successfully.")
            return {"type": "structured", "answer": answer, "related_websites": related_websites}
        
        elif question_type == "essay":
            # Generate an essay-style answer
            answer = generate_essay_answer(
                query=request.question,
                k=5,  # Default k for essay
                min_words=175,  # Default min words for essay
                max_words=300  # Default max words for essay
            )

            related_websites = get_related_websites(request.question)
            logging.info("Essay answer generated successfully.")
            return {"type": "essay", "answer": answer, "related_websites": related_websites}
        
        else:
            # Invalid type provided
            logging.error("Invalid question type provided.")
            raise HTTPException(status_code=400, detail="Invalid question type. Use 'structured' or 'essay'.")
    except Exception as e:
        logging.error(f"Error while generating answer: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while generating the answer.")

@app.post("/evaluate-answer")
def evaluate_answer(request: EvaluationRequest):
    """
    API endpoint to evaluate a user's answer based on the question type.
    """
    logging.info(f"Received request to evaluate answer: {request.dict()}")

    available, message = check_user_availability(request.student_id)
    if not available:
        raise HTTPException(status_code=404, detail="User not found.")
    
    is_acceptable, moderation_message = moderate_question(request.question)
    if not is_acceptable:
        logging.warning(f"Question moderated: {moderation_message}")
        raise HTTPException(status_code=400, detail=moderation_message)
    
    try:
        # Call the `evaluate_user_answer` function
        result = evaluate_user_answer(
            student_id=request.student_id,
            question=request.question,
            user_answer=request.user_answer,
            question_type=request.question_type
        )

        related_websites = get_related_websites(request.question)
        logging.info("User answer evaluated successfully.")
        return {
            "status": "success",
            "question": result["question"],
            "question_type": result["question_type"],
            "user_answer": result["user_answer"],
            "model_answer": result["model_answer"],
            "evaluation_result": result["evaluation_result"],
            "related_websites": related_websites
        }
    except ValueError as e:
        # Handle invalid question type or other validation errors
        logging.error(f"Validation error while evaluating answer: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Handle unexpected errors
        logging.error(f"Unexpected error while evaluating answer: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@app.post("/student-analytics")
def student_analytics(request: StudentEvaluationRequest):
    """
    API endpoint to get detailed analytics for a specific student.
    """
    logging.info(f"Received request for student analytics: {request.dict()}")

    available, message = check_user_availability(request.student_id)
    if not available:
        raise HTTPException(status_code=404, detail="User not found.")
    
    try:
        # Get the analytic details for the student
        analytics = get_student_analytic_details(request.student_id)
        
        if "message" in analytics:
            # Handle case where no data is found
            logging.warning(f"No data found for student_id: {request.student_id}")
            raise HTTPException(status_code=404, detail=analytics["message"])
        
        # Convert ObjectId fields to strings
        analytics = convert_objectid(analytics)

        logging.info(f"Analytics generated successfully for student_id: {request.student_id}")
        return {"status": "success", "student_id": request.student_id, "analytics": analytics}
    except Exception as e:
        logging.error(f"Error while generating student analytics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while retrieving student analytics.")


GOOGLE_API_KEY = os.getenv("API_KEY")
GOOGLE_CX_ID = os.getenv("CX_ID")
def get_related_websites(query: str, api_key: str = GOOGLE_API_KEY, cx: str = GOOGLE_CX_ID, max_results: int = 5):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cx,
        "q": query,
        "num": max_results
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return [item.get("link") for item in data.get("items", []) if item.get("link")]
    except requests.RequestException as e:
        logging.error(f"Google CSE API request failed: {e}")
    return []
    
@app.get("/get-student-question/{student_id}")
def get_student_question(student_id: str):
    """
    Retrieve the question assigned to a student for today.
    """
    logging.info(f"Fetching question for student_id: {student_id}")

    available, message = check_user_availability(student_id)
    if not available:
        raise HTTPException(status_code=404, detail="User not found.")

    try:
        record = get_questions_by_student_id(student_id)
        return {
            "student_id": student_id,
            "questions": record
        }
    except Exception as e:
        logging.error(f"Error fetching question for student_id {student_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error fetching question.")

@app.post("/evaluate-passpaper-answer")
def evaluate_student_answer(request: EvaluationRequest):
    """
    Evaluate a student's answer using the stored question.
    """
    logging.info(f"Received request to evaluate answer: {request.dict()}")
    
    available, message = check_user_availability(request.student_id)
    if not available:
        raise HTTPException(status_code=404, detail="User not found.")
    
    try:
        # Call the `evaluate_user_answer` function
        result = compare_with_passpaper_answer(
            student_id= request.student_id,
            question=request.question,
            user_answer=request.user_answer,
            question_type=request.question_type
        )

        related_websites = get_related_websites(request.question)
        logging.info("User answer evaluated successfully.")
        return {
            "status": "success",
            "question": result["question"],
            "question_type": result["question_type"],
            "user_answer": result["user_answer"],
            "model_answer": result["model_answer"],
            "evaluation_result": result["evaluation_result"],
            "related_websites": related_websites
        }
    except ValueError as e:
        # Handle invalid question type or other validation errors
        logging.error(f"Validation error while evaluating answer: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Handle unexpected errors
        logging.error(f"Unexpected error while evaluating answer: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
@app.post("/student-mind-map")
def student_mind_map(request: StudentEvaluationRequest):
    """
    Generate a node-link graph structure grouped by topic for mind map rendering.
    """
    logging.info(f"Received request to generate mind map for student: {request.student_id}")

    available, message = check_user_availability(request.student_id)
    if not available:
        raise HTTPException(status_code=404, detail="User not found.")

    try:
        analytics = get_student_analytic_details(request.student_id)

        if not analytics or "matched_study_materials" not in analytics:
            raise HTTPException(status_code=404, detail="No matched notes found for student.")

        matched_notes = pd.DataFrame(analytics["matched_study_materials"])
        if matched_notes.empty:
            raise HTTPException(status_code=404, detail="No relevant notes found to generate mind map.")

        mind_map = generate_mind_map(request.student_id)

        return {
            "status": "success",
            "student_id": request.student_id,
            "mind_map": mind_map
        }

    except HTTPException as http_exc:
        raise http_exc  # Reraise FastAPI-aware exceptions

    except Exception as e:
        logging.error(f"Failed to generate mind map for {request.student_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate mind map.")
    
@app.get("/")
def root():
    """
    Health check endpoint to ensure the API is running.
    """
    logging.info("Health check endpoint accessed.")
    return {"message": "Question and Answer API is running!"}
