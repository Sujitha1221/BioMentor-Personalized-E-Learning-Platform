import os
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException,Response, Request
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext
from database.database import users_collection, quizzes_collection
from bson import ObjectId
from bson.json_util import dumps
from utils.user_mgmt_methods import create_access_token, verify_password, create_refresh_token
from jose import JWTError, jwt

router = APIRouter()
load_dotenv() # Load environment variables
# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Secret & Algorithm
SECRET_KEY = os.getenv("SECRET_KEY", "biomentor2k25")
ALGORITHM = "HS256"

# User Registration Model
class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=50, pattern="^[A-Za-z ]+$")
    username: str = Field(..., min_length=3, max_length=20, pattern="^[a-zA-Z0-9_]+$")
    password: str
    email: EmailStr
    education_level: str
    
# User Login Model
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Create User Route
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


# Login Route with Refresh Token
@router.post("/login")
def login_user(user: UserLogin, response: Response):
    existing_user = users_collection.find_one({"email": user.email})
    
    if not existing_user or not verify_password(user.password, existing_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": str(existing_user["_id"]), "username": existing_user["username"]})
    refresh_token = create_refresh_token(data={"sub": str(existing_user["_id"])})

    # Store Refresh Token in HTTP-only cookie
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, samesite="Lax")

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(existing_user["_id"]),
        "username": existing_user["username"]
    }

# refresh token route
@router.post("/refresh")
def refresh_token(request: Request):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token found")

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        new_access_token = create_access_token(data={"sub": user_id})
        return {"access_token": new_access_token, "token_type": "bearer"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

# Check if the user has any previous quizzes
@router.get("/users/{user_id}/has_previous_quiz")
def check_user_quiz_history(user_id: str):
    """
    Check if the user has any previous quizzes by searching in the `quizzes` collection.
    Returns True if at least one quiz exists.
    """
    try:
        # Ensure the user exists
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        # Check if the user has any quizzes
        quiz_count = quizzes_collection.count_documents({"user_id": user_id})
        
        return {"has_previous_quiz": quiz_count > 0}

    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
