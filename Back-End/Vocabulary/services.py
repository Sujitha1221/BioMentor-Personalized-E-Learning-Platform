import random
import logging
from datetime import datetime, timedelta
from database import db
from utils.review_quality import word_accuracy
from bson import ObjectId

async def assign_daily_questions():
    """Assign exactly 10 random flashcards from MongoDB."""
    cursor = db["flashcards"].aggregate([{"$sample": {"size": 10}}])
    questions = await cursor.to_list(length=10)

    # Convert ObjectId to string
    for q in questions:
        q["_id"] = str(q["_id"])

    return questions

async def get_daily_questions(user_id):
    """Fetch up to 10 daily vocabulary words for a user based on spaced repetition."""
    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user:
        return {"error": "User not found"}

    today = datetime.utcnow().date()
    due_questions = []

    # Debugging step: Check what user["history"] contains
    print("User history:", user.get("history", []))

    # Ensure history is a list
    if not isinstance(user.get("history", []), list):
        return {"error": "History is not a list"}

    # Collect words due for review
    for entry in user.get("history", []):
        if isinstance(entry, dict) and "next_review" in entry:
            if datetime.strptime(entry["next_review"], "%Y-%m-%d").date() <= today:
                due_questions.append(ObjectId(entry["question_id"]))

    # Fetch due words from MongoDB
    questions = await db["flashcards"].find({"_id": {"$in": due_questions}}).to_list(len(due_questions))

    # Convert _id to string
    seen_ids = {str(q["_id"]) for q in questions}

    # If fewer than 10, fetch additional new ones
    remaining_slots = max(0, 10 - len(questions))
    if remaining_slots > 0:
        cursor = db["flashcards"].aggregate([
            {"$match": {"_id": {"$nin": list(seen_ids)}}},
            {"$sample": {"size": remaining_slots}}
        ])
        new_questions = await cursor.to_list(length=remaining_slots)
        questions.extend(new_questions)

    # Strictly limit to 10 questions
    questions = questions[:10]

    # Convert ObjectId to string for JSON serialization
    for q in questions:
        q["_id"] = str(q["_id"])

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

    # ✅ Ensure history is a list before iterating
    if not isinstance(user.get("history", []), list):
        return {"error": "User history is not a list"}

    print("User history:", user["history"])  # Debugging step

    # Check if question exists in user history
    history_entry = next(
        (h for h in user["history"] if isinstance(h, dict) and h.get("question_id") == str(question_id)), 
        None
    )

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


async def add_score(username: str, score: int):
    """Insert or update the user's score and return their new rank."""
    
    # Check if the user already exists
    existing_entry = await db["leaderboard"].find_one({"username": username})

    if existing_entry:
        # If the new score is higher, update it
        if score > existing_entry["score"]:
            await db["leaderboard"].update_one(
                {"username": username},
                {"$set": {"score": score}}
            )
    else:
        # Insert a new leaderboard entry
        await db["leaderboard"].insert_one({
            "username": username,
            "score": score
        })

    # Calculate rank
    return await get_rank(username)

async def get_rank(username: str):
    """Get the rank of a user based on their score."""

    # Get sorted leaderboard
    leaderboard = await db["leaderboard"].find().sort("score", -1).to_list(None)

    # Ensure ObjectId is converted to string for JSON serialization
    for entry in leaderboard:
        entry["_id"] = str(entry["_id"])

    # Find user's rank
    rank = next((index + 1 for index, entry in enumerate(leaderboard) if entry["username"] == username), None)

    return {
        "rank": rank,
        "top_5": leaderboard[:5]  # Get top 5 scores
    }

async def get_top_5():
    """Retrieve the top 5 scores from the leaderboard."""
    top_scores = await db["leaderboard"].find().sort("score", -1).limit(5).to_list(None)

    # Convert ObjectId to string for proper JSON serialization
    for entry in top_scores:
        entry["_id"] = str(entry["_id"])

    return {"top_5": top_scores}

async def get_user_stats(user_id):
    """Display detailed stats about a user's review history."""
    from collections import Counter

    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user:
        return {"error": "User not found"}

    history = user.get("history", [])
    if not isinstance(history, list):
        return {"error": "User history is not valid"}

    total_reviews = len(history)
    total_score = sum(entry.get("review_score", 0) for entry in history)
    average_score = round(total_score / total_reviews, 2) if total_reviews > 0 else 0

    # Count each score level
    score_distribution = Counter(entry.get("review_score", 0) for entry in history)

    # Count next review dates
    review_schedule = Counter(entry.get("next_review", "N/A") for entry in history)

    return {
        "user_id": str(user["_id"]),
        "username": user.get("username"),
        "total_score": user.get("total_score", 0),
        "total_reviews": total_reviews,
        "average_score": average_score,
        "score_distribution": dict(score_distribution),
        "review_schedule": dict(review_schedule)
    }
