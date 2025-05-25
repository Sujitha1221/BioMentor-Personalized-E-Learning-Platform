import os
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from service import UserService, UserCreate, UserUpdate
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException,Response, Depends
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext
from dotenv import load_dotenv
from jose import JWTError, jwt
import logging
from database import users_collection
from user_mgmt_methods import create_access_token, verify_password, create_refresh_token

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

user_service = UserService()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://20.193.152.91","http://localhost:3000"],  # Adjust this to your frontend URL for better security
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Load SECRET_KEY & ALGORITHM from .env
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

# Ensure they are loaded properly
if not SECRET_KEY or not ALGORITHM:
    raise ValueError("SECRET_KEY or ALGORITHM is missing in the .env file!")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
@app.post("/register")
def register_user(user: UserRegister):
    hashed_password = pwd_context.hash(user.password)

    existing_user = users_collection.find_one({"$or": [{"username": user.username}, {"email": user.email}]})
    if existing_user:
        logging.error(f" Username or email already exists: {user.username}, {user.email}")
        raise HTTPException(status_code=400, detail="Username or email already exists") 
        
    new_user = {
        "username": user.username,
        "password": hashed_password,
        "email": user.email,
        "full_name": user.full_name,
        "education_level": user.education_level,
        "performance": {  # Track accuracy & time for each difficulty level
            "total_quizzes": 0,
            "accuracy_easy": 0, "accuracy_medium": 0, "accuracy_hard": 0,
            "time_easy": 0, "time_medium": 0, "time_hard": 0,
            "strongest_area": None, "weakest_area": None,
            "last_10_quizzes": [],
            "consistency_score": 0
        }
    }
    result = users_collection.insert_one(new_user)
    return {"message": "User registered successfully!", "user_id": str(result.inserted_id)}


# Login Route with Refresh Token
@app.post("/login")
def login_user(user: UserLogin, response: Response):
    existing_user = users_collection.find_one({"email": user.email})
    
    if not existing_user or not verify_password(user.password, existing_user["password"]):
        logging.error(f" Invalid email or password: {user.email}")
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": str(existing_user["_id"]), "username": existing_user["username"]})
    refresh_token = create_refresh_token(data={"sub": str(existing_user["_id"])})

    # Store Refresh Token in HTTP-only cookie
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, samesite="Lax")

    return {
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": str(existing_user["_id"]),
        "username": existing_user["username"]
    }

# refresh token route
@app.post("/refresh")
def refresh_token(data: dict):
    refresh_token = data.get("refresh_token")  # Read from request body

    if not refresh_token:
        logging.error(" No refresh token provided")
        raise HTTPException(status_code=401, detail="No refresh token provided")

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        new_access_token = create_access_token(data={"sub": user_id})
        
        return {"access_token": new_access_token, "token_type": "bearer"}
    except JWTError:
        logging.error(" Invalid or expired refresh token")
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

@app.get("/user_exists_by_email")
def check_user_exists_by_email(email: EmailStr):
    """
    Check if a user exists using an email address.
    """
    existing_user = users_collection.find_one({"email": email})
    exists = True if existing_user else False
    return {"exists": exists}
