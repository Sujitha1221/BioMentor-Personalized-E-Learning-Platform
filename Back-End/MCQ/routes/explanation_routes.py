# routes/explanation_routes.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict
from utils.user_mgmt_methods import get_current_user
from utils.explanation.explanation_helper import explain_mcq, verify_answer_by_generation, is_inappropriate, is_biology_question

router = APIRouter()

class MCQExplainRequest(BaseModel):
    question: str
    options: Dict[str, str]

class MCQVerifyRequest(BaseModel):
    question: str
    options: Dict[str, str]
    claimed_answer: str

@router.post("/mcq/explain_only")
def explain_only(request: MCQExplainRequest):
    if is_inappropriate(request.question):
        raise HTTPException(status_code=400, detail="Question contains inappropriate or harmful content.")
    if not is_biology_question(request.question):
        raise HTTPException(status_code=400, detail="Only biology-related questions are supported.")
    try:
        return explain_mcq(request.question, request.options)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mcq/verify_and_explain")
def verify_and_explain(request: MCQVerifyRequest):
    if is_inappropriate(request.question):
        raise HTTPException(status_code=400, detail="Question contains inappropriate or harmful content.")
    if not is_biology_question(request.question):
        raise HTTPException(status_code=400, detail="Only biology-related questions are supported.")
    try:
        return verify_answer_by_generation(request.question, request.options, request.claimed_answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
