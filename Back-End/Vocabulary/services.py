import random
import logging
from datetime import datetime, timedelta
from database import db
from utils.review_quality import word_accuracy
from bson import ObjectId

async def assign_daily_questions():
    """Assign 20 random flashcards from MongoDB."""
    cursor = db["flashcards"].aggregate([{"$sample": {"size": 20}}])
    questions = await cursor.to_list(length=20)

    # ✅ Convert ObjectId to string
    for q in questions:
        q["_id"] = str(q["_id"])

    return questions

async def get_daily_questions(user_id):
    """Fetch daily vocabulary words for a user based on spaced repetition."""
    from datetime import datetime

    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user:
        return {"error": "User not found"}

    today = datetime.utcnow().date()
    due_questions = []

    # Collect words due for review
    for entry in user["history"]:
        if datetime.strptime(entry["next_review"], "%Y-%m-%d").date() <= today:
            due_questions.append(entry["question_id"])

    # Fetch words from MongoDB
    questions = await db["flashcards"].find({"_id": {"$in": [ObjectId(qid) for qid in due_questions]}}).to_list(len(due_questions))

    # If fewer than 20, add new ones
    if len(questions) < 20:
        seen_ids = [q["_id"] for q in questions]
        cursor = db["flashcards"].aggregate([
            {"$match": {"_id": {"$nin": seen_ids}}},
            {"$sample": {"size": 20 - len(questions)}}
        ])
        new_questions = await cursor.to_list(length=20 - len(questions))
        questions.extend(new_questions)

    for q in questions:
        q["_id"] = str(q["_id"])  # Convert ObjectId to string

    return {"questions": questions}


async def update_progress(user_id, question_id, user_answer):
    """Update spaced repetition progress for a specific user."""
    from datetime import datetime, timedelta
    from utils.review_quality import word_accuracy

    # Fetch the vocabulary word
    question = await db["flashcards"].find_one({"_id": ObjectId(question_id)})
    if not question:
        return {"error": "Question not found"}

    # ✅ Compare with vocabulary word, not the hint
    review_score = word_accuracy(question["question"], user_answer)

    # Fetch or create user record
    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user:
        user = {
            "_id": ObjectId(user_id),
            "username": f"user_{user_id}",  # Temporary username
            "total_score": 0,
            "history": []
        }
        await db["users"].insert_one(user)

    # Check if question exists in user history
    history_entry = next((h for h in user["history"] if h["question_id"] == str(question_id)), None)

    if history_entry is None:
        # If first time seeing the word, create a new entry
        next_review = datetime.utcnow() + timedelta(days=1)
        history_entry = {
            "question_id": str(question_id),
            "times_seen": 1,
            "review_score": review_score,
            "next_review": next_review.strftime("%Y-%m-%d")
        }
        await db["users"].update_one(
            {"_id": ObjectId(user_id)},
            {"$push": {"history": history_entry}, "$inc": {"total_score": review_score}}
        )
    else:
        # Update existing entry
        history_entry["times_seen"] += 1
        history_entry["review_score"] = review_score

        # ✅ Implement **Spaced Repetition (SM-2 Algorithm)**
        if review_score == 5:
            interval = 10  # Maximum interval
        elif review_score >= 4:
            interval = 5
        elif review_score >= 3:
            interval = 3
        elif review_score >= 2:
            interval = 2
        else:
            interval = 1  # Immediate review required

        history_entry["next_review"] = (datetime.utcnow() + timedelta(days=interval)).strftime("%Y-%m-%d")

        await db["users"].update_one(
            {"_id": ObjectId(user_id), "history.question_id": str(question_id)},
            {"$set": {"history.$": history_entry}, "$inc": {"total_score": review_score}}
        )

    return {
        "review_score": review_score,
        "next_review": history_entry["next_review"]
    }
