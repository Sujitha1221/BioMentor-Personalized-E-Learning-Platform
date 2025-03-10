from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from database.database import users_collection
from bson import ObjectId
from bson.json_util import dumps
import json

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User Registration Model
class UserRegister(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: str
    education_level: str

@router.post("/register")
def register_user(user: UserRegister):
    hashed_password = pwd_context.hash(user.password)

    existing_user = users_collection.find_one({"$or": [{"username": user.username}, {"email": user.email}]})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    new_user = {
        "username": user.username,
        "password": hashed_password,
        "email": user.email,
        "full_name": user.full_name,
        "education_level": user.education_level,
        "performance": {  # Track accuracy & time for each difficulty level
            "easy_correct": 0, "easy_total": 0, "easy_time": 0,
            "medium_correct": 0, "medium_total": 0, "medium_time": 0,
            "hard_correct": 0, "hard_total": 0, "hard_time": 0,
            "history": []  # Store past quizzes (last 5)
        }
    }
    result = users_collection.insert_one(new_user)
    return {"message": "User registered successfully!", "user_id": str(result.inserted_id)}

@router.get("/users", response_model=list)
def get_all_users():
    """Fetch all users from the database."""
    try:
        users = list(users_collection.find({}, {"password": 0}))  # Exclude passwords for security
        if not users:
            raise HTTPException(status_code=404, detail="No users found.")

        return json.loads(dumps(users))  # Convert BSON to JSON

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
