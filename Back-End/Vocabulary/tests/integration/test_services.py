import pytest
from datetime import datetime, timedelta
from bson import ObjectId

from database import db
from services import (
    assign_daily_questions,
    get_daily_questions,
    update_progress,
    add_score,
    get_rank,
    get_top_5,
    get_user_stats
)

pytestmark = pytest.mark.asyncio

@pytest.fixture
async def setup_test_data():
    """Set up test data for services tests."""
    # Clear existing data
    await db["flashcards"].delete_many({})
    await db["users"].delete_many({})
    await db["leaderboard"].delete_many({})
    
    # Insert test flashcards
    test_flashcards = [
        {
            "_id": ObjectId(),
            "question": "What is photosynthesis?",
            "answer": "Process by which plants make food"
        },
        {
            "_id": ObjectId(),
            "question": "What is mitosis?",
            "answer": "Cell division process"
        }
    ]
    await db["flashcards"].insert_many(test_flashcards)
    
    # Insert test user
    test_user = {
        "_id": ObjectId(),
        "username": "test_user",
        "total_score": 0,
        "history": []
    }
    await db["users"].insert_one(test_user)
    
    return str(test_user["_id"])

async def test_assign_daily_questions():
    """Test assigning daily questions."""
    questions = await assign_daily_questions()
    assert len(questions) == 10
    assert all("_id" in q for q in questions)
    assert all("question" in q for q in questions)
    assert all("answer" in q for q in questions)

async def test_get_daily_questions(setup_test_data):
    """Test getting daily questions for a user."""
    user_id = await setup_test_data
    result = await get_daily_questions(user_id)
    assert "questions" in result
    assert len(result["questions"]) <= 10

async def test_update_progress(setup_test_data):
    """Test updating user progress."""
    user_id = await setup_test_data
    question_id = str((await db["flashcards"].find_one())["_id"])
    
    result = await update_progress(user_id, question_id, "test answer")
    assert "review_score" in result
    assert "next_review" in result
    
    # Verify user history was updated
    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    assert len(user["history"]) == 1
    assert user["history"][0]["question_id"] == question_id

async def test_add_score():
    """Test adding a score to the leaderboard."""
    # Clear leaderboard first
    await db["leaderboard"].delete_many({})
    
    result = await add_score("test_user", 100)
    assert "rank" in result
    assert "top_5" in result
    
    # Verify score was added
    entry = await db["leaderboard"].find_one({"username": "test_user"})
    assert entry is not None
    assert entry["score"] == 100

async def test_get_rank():
    """Test getting user rank."""
    # Clear leaderboard first
    await db["leaderboard"].delete_many({})
    
    # Add multiple scores
    await add_score("user1", 100)
    await add_score("user2", 200)
    
    result = await get_rank("user1")
    assert "rank" in result
    assert "top_5" in result
    assert result["rank"] == 2  # Second place

async def test_get_top_5():
    """Test getting top 5 scores."""
    # Clear leaderboard first
    await db["leaderboard"].delete_many({})
    
    # Add multiple scores
    await add_score("user1", 100)
    await add_score("user2", 200)
    await add_score("user3", 300)
    await add_score("user4", 400)
    await add_score("user5", 500)
    await add_score("user6", 600)
    
    result = await get_top_5()
    assert "top_5" in result
    assert len(result["top_5"]) == 5
    assert result["top_5"][0]["score"] == 600  # Highest score first

async def test_get_user_stats(setup_test_data):
    """Test getting user statistics."""
    user_id = await setup_test_data
    
    # Add some review history
    question_id = str((await db["flashcards"].find_one())["_id"])
    await update_progress(user_id, question_id, "test answer")
    
    stats = await get_user_stats(user_id)
    assert "user_id" in stats
    assert "username" in stats
    assert "total_score" in stats
    assert "total_reviews" in stats
    assert "average_score" in stats
    assert "score_distribution" in stats
    assert "review_schedule" in stats 