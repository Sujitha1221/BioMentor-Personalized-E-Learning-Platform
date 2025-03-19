from fastapi import APIRouter, HTTPException
from services import add_score, get_top_5

router = APIRouter()

@router.post("/add_score")
async def add_user_score(username: str, score: int):
    """Add a new score and return the user's rank."""
    if score < 0:
        raise HTTPException(status_code=400, detail="Score cannot be negative")
    
    result = await add_score(username, score)
    return result

@router.get("/top5")
async def get_leaderboard():
    """Retrieve the top 5 leaderboard entries."""
    return await get_top_5()
