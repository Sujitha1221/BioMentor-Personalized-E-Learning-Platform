# routes/explanation_routes.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict
from utils.user_mgmt_methods import get_current_user
from utils.explanation.explanation_helper import explain_mcq, verify_answer_by_generation

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
    try:
        return explain_mcq(request.question, request.options)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mcq/verify_and_explain")
def verify_and_explain(request: MCQVerifyRequest):
    try:
        return verify_answer_by_generation(request.question, request.options, request.claimed_answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
