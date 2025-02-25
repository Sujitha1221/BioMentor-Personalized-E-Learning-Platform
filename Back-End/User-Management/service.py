import bcrypt
import jwt
import datetime
import os
from pymongo import MongoClient
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables (for MongoDB URI and secret key)
load_dotenv()

# Secret key for JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client.user_management  # Database name
users_collection = db.users  # Collection name

# User Models
class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class UserUpdate(BaseModel):
    email: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserService:
    def create_user(self, user: UserCreate):
        # Check if user already exists
        if users_collection.find_one({"username": user.username}):
            return {"error": "User already exists"}

        # Hash password
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

        # Store user in MongoDB
        users_collection.insert_one({
            "username": user.username,
            "password": hashed_password,
            "email": user.email
        })
        return {"message": "User created successfully"}

    def get_user(self, username: str):
        user = users_collection.find_one({"username": username}, {"_id": 0, "password": 0})
        return user if user else {"error": "User not found"}

    def update_user(self, username: str, user_update: UserUpdate):
        if not users_collection.find_one({"username": username}):
            return {"error": "User not found"}

        users_collection.update_one(
            {"username": username},
            {"$set": {"email": user_update.email}}
        )
        return {"message": "User updated successfully"}

    def delete_user(self, username: str):
        result = users_collection.delete_one({"username": username})
        return {"message": "User deleted successfully"} if result.deleted_count > 0 else {"error": "User not found"}

    def login(self, username: str, password: str):
        user = users_collection.find_one({"username": username})
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user["password"]):
            return None

        # Generate JWT token
        token = jwt.encode(
            {"sub": username, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
            SECRET_KEY,
            algorithm="HS256"
        )
        return token

    def logout(self, token: str):
        # Simple logout implementation (extend as needed)
        return {"message": "User logged out"}
