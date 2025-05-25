import pytest
from datetime import datetime
from bson import ObjectId

from models import Flashcard, UserProgress, User, LeaderboardEntry

def test_flashcard_model():
    """Test Flashcard model creation and validation."""
    # Test with string ID
    flashcard = Flashcard(
        _id="507f1f77bcf86cd799439011",
        question="What is photosynthesis?",
        answer="Process by which plants make food"
    )
    assert flashcard.id == "507f1f77bcf86cd799439011"
    assert flashcard.question == "What is photosynthesis?"
    assert flashcard.answer == "Process by which plants make food"
    
    # Test with ObjectId
    obj_id = ObjectId()
    flashcard = Flashcard(
        _id=str(obj_id),  # Convert ObjectId to string
        question="What is mitosis?",
        answer="Cell division process"
    )
    assert flashcard.id == str(obj_id)

def test_user_progress_model():
    """Test UserProgress model creation and validation."""
    progress = UserProgress(
        _id="507f1f77bcf86cd799439011",
        total_score=100,
        history=[{"question_id": "123", "score": 5}]
    )
    assert progress.id == "507f1f77bcf86cd799439011"
    assert progress.total_score == 100
    assert len(progress.history) == 1
    assert progress.history[0]["question_id"] == "123"

def test_user_model():
    """Test User model creation and validation."""
    user = User(
        _id="507f1f77bcf86cd799439011",
        username="test_user",
        total_score=150,
        history=[{
            "question_id": "123",
            "times_seen": 2,
            "review_score": 4,
            "next_review": "2024-03-20"
        }]
    )
    assert user.id == "507f1f77bcf86cd799439011"
    assert user.username == "test_user"
    assert user.total_score == 150
    assert len(user.history) == 1
    assert user.history[0]["times_seen"] == 2

def test_leaderboard_entry_model():
    """Test LeaderboardEntry model creation and validation."""
    entry = LeaderboardEntry(
        _id="507f1f77bcf86cd799439011",
        username="top_user",
        score=1000
    )
    assert entry.id == "507f1f77bcf86cd799439011"
    assert entry.username == "top_user"
    assert entry.score == 1000 