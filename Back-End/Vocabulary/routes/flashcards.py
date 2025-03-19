from fastapi import APIRouter, HTTPException
from services import get_daily_questions, update_progress, add_score, get_top_5
from database import db
from pydantic import BaseModel
from bson import ObjectId

router = APIRouter()

class AnswerInput(BaseModel):
    user_answer: str

class ScoreUpdateInput(BaseModel):
    score: int

class ScoreEntry(BaseModel):
    """Model for adding a new score."""
    username: str
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

@router.post("/add_score")
async def add_user_score(score_entry: ScoreEntry):
    """Add a new score and return the user's rank."""
    if score_entry.score < 0:
        raise HTTPException(status_code=400, detail="Score cannot be negative")
    
    result = await add_score(score_entry.username, score_entry.score)
    return result

@router.get("/top5")
async def get_leaderboard():
    """Retrieve the top 5 leaderboard entries."""
    return await get_top_5()

# @router.get("/leaderboard")
# async def get_leaderboard():
#     """Fetch top users by total score."""
#     try:
#         cursor = db["users"].find({}, {"_id": 1, "username": 1, "total_score": 1})
#         scores = await cursor.to_list(length=None)

#         if not scores:
#             raise HTTPException(status_code=404, detail="No leaderboard data available.")

#         # Convert ObjectId to string and handle missing total_score
#         leaderboard = []
#         for user in scores:
#             leaderboard.append({
#                 "_id": str(user["_id"]),  # Convert _id to string
#                 "username": user.get("username", "Unknown User"),  # Handle missing username
#                 "total_score": user.get("total_score", 0)  # Default to 0 if missing
#             })

#         # Sort by total_score in descending order
#         leaderboard = sorted(leaderboard, key=lambda x: x["total_score"], reverse=True)

#         return {"leaderboard": leaderboard[:10]}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error fetching leaderboard: {str(e)}")


# @router.post("/leaderboard/update/{user_id}")
# async def update_user_score(user_id: str, score_update: ScoreUpdateInput):
#     """Update a user's total score and refresh the leaderboard."""
#     user = await db["users"].find_one({"_id": ObjectId(user_id)})
    
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     # Update the user's score
#     await db["users"].update_one(
#         {"_id": ObjectId(user_id)},
#         {"$inc": {"total_score": score_update.score}}
#     )

#     # Retrieve the updated user info
#     updated_user = await db["users"].find_one({"_id": ObjectId(user_id)}, {"_id": 1, "username": 1, "total_score": 1})

#     return {
#         "message": "Score updated successfully",
#         "user": {
#             "_id": str(updated_user["_id"]),  # Convert ObjectId to string
#             "username": updated_user["username"],
#             "total_score": updated_user["total_score"]
#         }
#     }


