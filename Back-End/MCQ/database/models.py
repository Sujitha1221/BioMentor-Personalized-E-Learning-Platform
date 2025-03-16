from pydantic import BaseModel, EmailStr
from typing import List, Dict
from bson import ObjectId

# Helper function to convert ObjectId to string
def object_id_str(obj_id):
    return str(obj_id) if isinstance(obj_id, ObjectId) else obj_id

# Pydantic model for User
class User(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: str
    education_level: str

# Pydantic model for Quiz Question
class Question(BaseModel):
    question_text: str
    options: Dict[str, str]  # Example: {"A": "Option 1", "B": "Option 2"}
    correct_answer: str
    difficulty: str
    b: float  # Difficulty parameter (IRT)
    a: float  # Discrimination parameter (IRT)
    c: float  # Guessing parameter (IRT)


# Pydantic model for Quiz
class Quiz(BaseModel):
    user_id: str  # Will store ObjectId as string
    questions: List[Question]

    def dict(self, **kwargs):
        """Ensure user_id is a string ObjectId"""
        quiz_dict = super().dict(**kwargs)
        quiz_dict["user_id"] = object_id_str(quiz_dict["user_id"])
        return quiz_dict

# Pydantic model for User Response
class UserResponse(BaseModel):
    user_id: str
    quiz_id: str
    question_id: str
    selected_answer: str
    is_correct: bool
    time_taken: int
    difficulty: str

    def dict(self, **kwargs):
        """Ensure all MongoDB ObjectIds are converted to strings"""
        response_dict = super().dict(**kwargs)
        response_dict["user_id"] = object_id_str(response_dict["user_id"])
        response_dict["quiz_id"] = object_id_str(response_dict["quiz_id"])
        response_dict["question_id"] = object_id_str(response_dict["question_id"])
        return response_dict
