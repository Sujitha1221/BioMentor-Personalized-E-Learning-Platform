from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from database.database import users_collection
from bson import ObjectId

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

    # Check if the user already exists
    existing_user = users_collection.find_one({"$or": [{"username": user.username}, {"email": user.email}]})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    # Insert new user into MongoDB
    new_user = {
        "username": user.username,
        "password": hashed_password,
        "email": user.email,
        "full_name": user.full_name,
        "education_level": user.education_level
    }
    result = users_collection.insert_one(new_user)

    return {"message": "User registered successfully!", "user_id": str(result.inserted_id)}
