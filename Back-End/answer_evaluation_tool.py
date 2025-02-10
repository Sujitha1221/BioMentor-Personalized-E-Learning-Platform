import logging
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

# MongoDB Connection
def get_db():
    """
    Connect to MongoDB and return the database object.
    """
    try:
        client = MongoClient("mongodb://localhost:27017/")  # Update with your MongoDB URI
        db = client["evaluation_db"]
        logging.info("Connected to MongoDB successfully.")
        return db
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {e}", exc_info=True)
        raise

db = get_db()

# Save Evaluation Data
def save_evaluation(student_id, question, question_type, user_answer, model_answer, evaluation_result):
    """
    Save evaluation data to MongoDB.
    """
    try:
        collection = db["evaluations"]
        record = {
            "student_id": student_id,
            "question": question,
            "question_type": question_type,
            "user_answer": user_answer,
            "model_answer": model_answer,
            "evaluation_result": evaluation_result,
            "timestamp": datetime.utcnow()
        }
        collection.insert_one(record)
        logging.info(f"Evaluation data saved for student_id: {student_id}")
    except Exception as e:
        logging.error(f"Error saving evaluation data: {e}", exc_info=True)
        raise

