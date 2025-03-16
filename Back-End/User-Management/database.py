import os
import time
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# Load environment variables
load_dotenv()

MONGO_URI = "mongodb+srv://Y3S1:y3s1spm@spm.pbmlqx7.mongodb.net/mcq_quiz_platform?retryWrites=true&w=majority" # Default in case .env is missing

# Connect to MongoDB Atlas with retry mechanism
while True:
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client.get_database("mcq_quiz_platform")  # Update database name if needed
        users_collection = db["users"]
        print(" Connected to MongoDB Atlas")
        break
    except ConnectionFailure as e:
        print(" Database connection failed:", e)
        time.sleep(2)  # Retry every 2 seconds
