from datetime import datetime
from pydantic import BaseModel, Field
from bson import ObjectId
from typing import List, Optional
from datetime import datetime

class Flashcard(BaseModel):
    id: str = Field(alias="_id")  # MongoDB _id mapped to id
    question: str
    answer: str

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

class UserProgress(BaseModel):
    id: str = Field(alias="_id")
    total_score: int = 0
    history: list = []

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

class User(BaseModel):
    """User model for tracking spaced repetition progress."""
    id: str = Field(alias="_id")  # MongoDB _id field
    username: str  # Unique username
    total_score: int = 0  # Overall user score
    history: List[dict] = []  # List of reviewed words with scores and next review

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}


class LeaderboardEntry(BaseModel):
    id: str = Field(alias="_id")  # MongoDB _id mapped to id
    username: str  # User's name
    score: int  # Total score

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}