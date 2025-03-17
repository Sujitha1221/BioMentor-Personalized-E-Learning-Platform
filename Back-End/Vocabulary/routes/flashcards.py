from fastapi import APIRouter, HTTPException
from services import get_daily_questions, update_progress
from database import db
from pydantic import BaseModel
from bson import ObjectId

router = APIRouter()

class AnswerInput(BaseModel):
    user_answer: str

class ScoreUpdateInput(BaseModel):
    score: int

@router.get("/daily/{user_id}")
async def fetch_daily_questions(user_id: str):
    """Get today's vocabulary words based on spaced repetition for a user."""
    response = await get_daily_questions(user_id)
    return response

@router.post("/answer/{user_id}/{question_id}")
async def submit_answer(user_id: str, question_id: str, answer: AnswerInput):
    """Submit an answer and update spaced repetition progress."""
    result = await update_progress(user_id, question_id, answer.user_answer)
    return result

@router.get("/leaderboard")
async def get_leaderboard():
    """Fetch top users by total score."""
    cursor = db["users"].find({}, {"_id": 1, "username": 1, "total_score": 1})
    scores = await cursor.to_list(length=None)
    scores.sort(key=lambda x: x["total_score"], reverse=True)
    
    return {"leaderboard": scores[:10]}


@router.post("/leaderboard/update/{user_id}")
async def update_user_score(user_id: str, score_update: ScoreUpdateInput):
    """Update a user's total score and refresh the leaderboard."""
    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db["users"].update_one(
        {"_id": ObjectId(user_id)},
        {"$inc": {"total_score": score_update.score}}
    )

    return {"message": "Score updated successfully"}
