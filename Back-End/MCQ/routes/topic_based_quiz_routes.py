from fastapi import APIRouter, HTTPException, Query, Depends
from datetime import datetime
import pandas as pd
import torch
import os
import random
from pydantic import BaseModel
from typing import List
from sentence_transformers import util
from bson import ObjectId
from database.database import unit_quizzes, unit_quiz_responses, users_collection
from utils.model_loader import embedding_model
from utils.user_mgmt_methods import get_current_user

router = APIRouter()

# Load dataset
DATASET_PATH = "dataset/unit-wise-dataset/unit_tagged_mcq_dataset.csv"
EMBEDDING_PATH = "dataset/unit-wise-dataset/unit_question_embeddings.pt"
unit_df = pd.read_csv(DATASET_PATH).fillna("")

if os.path.exists(EMBEDDING_PATH):
    embeddings = torch.load(EMBEDDING_PATH, weights_only=False)
else:
    embeddings = unit_df["Question Text"].apply(lambda x: embedding_model.encode(x, convert_to_tensor=True))
    torch.save(embeddings, EMBEDDING_PATH)

unit_df["embedding"] = embeddings

class QuizResponse(BaseModel):
    question_text: str
    selected_answer: str

class SubmitUnitQuizRequest(BaseModel):
    quiz_id: str
    responses: List[QuizResponse]

# Helper: Format question
def format_question(row):
    options = {
        "A": row["Option 1"],
        "B": row["Option 2"],
        "C": row["Option 3"],
        "D": row["Option 4"],
        "E": row["Option 5"]
    }
    correct_text = row["Correct Answer"].strip()
    correct_label = next((k for k, v in options.items() if v.strip() == correct_text), None)

    return {
        "question_text": row["Question Text"],
        "options": options,
        "correct_answer": correct_label,
        "difficulty": row.get("Difficulty Level", "medium")
    }

# Helper: Get previously seen questions
def get_previously_seen_questions(user_id, unit_name):
    responses = unit_quiz_responses.find({"user_id": user_id, "unit_name": unit_name})
    return set(q["question_text"] for r in responses for q in r["responses"])

# Helper: Fallback similar questions
def get_semantically_similar_questions(target_texts, excluded_units, used_questions, count):
    candidates = unit_df[~unit_df["Assigned_Unit"].isin(excluded_units)]
    candidates = candidates[~candidates["Question Text"].isin(used_questions)]
    if candidates.empty:
        return []
    target_embeddings = embedding_model.encode(target_texts, convert_to_tensor=True)
    results = []
    for _, row in candidates.iterrows():
        sim = util.cos_sim(row["embedding"], target_embeddings).max().item()
        results.append((sim, row))
    results = sorted(results, key=lambda x: x[0], reverse=True)[:count]
    return [format_question(row) for _, row in results]

# Route: Generate Quiz
@router.get("/unit_quiz/generate/{user_id}")
def generate_unit_quiz(
    user_id: str,
    unit: str = Query(...),
    question_count: int = Query(10, ge=1, le=100),
    current_user: str = Depends(get_current_user)
):
    existing_user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found. Please register before generating a quiz.")
        
    if current_user != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    
    filtered = unit_df[unit_df["Assigned_Unit"] == unit]
    if filtered.empty:
        raise HTTPException(status_code=404, detail=f"No questions found for {unit}.")

    used_questions = get_previously_seen_questions(current_user, unit)
    filtered = filtered[~filtered["Question Text"].isin(used_questions)]

    sampled_questions = []
    seen = set()
    attempts = 0
    max_attempts = 100
    clusters = list(filtered["Cluster"].unique()) if "Cluster" in filtered.columns else [None]
    random.shuffle(clusters)

    while len(sampled_questions) < question_count and attempts < max_attempts:
        cluster = random.choice(clusters)
        cluster_qs = filtered[filtered["Cluster"] == cluster] if cluster else filtered
        if not cluster_qs.empty:
            q = cluster_qs.sample(1).iloc[0]
            q_text = q["Question Text"]
            if q_text not in seen:
                sampled_questions.append(format_question(q))
                seen.add(q_text)
        attempts += 1

    if len(sampled_questions) < question_count:
        needed = question_count - len(sampled_questions)
        fallback_questions = get_semantically_similar_questions(
            [q["question_text"] for q in sampled_questions],
            excluded_units=[unit],
            used_questions=used_questions.union(seen),
            count=needed
        )
        sampled_questions.extend(fallback_questions)

    quiz_entry = {
        "user_id": current_user,
        "unit_name": unit,
        "questions": sampled_questions,
        "created_at": datetime.utcnow()
    }
    quiz_id = unit_quizzes.insert_one(quiz_entry).inserted_id

    return {
        "message": f"Quiz generated for {unit}",
        "quiz_id": str(quiz_id),
        "questions": sampled_questions
    }

@router.post("/quiz/submit/{user_id}")
def submit_unit_quiz(
    user_id: str,
    request: SubmitUnitQuizRequest,
    current_user: str = Depends(get_current_user)
):
    quiz_id = request.quiz_id
    responses = request.responses

    # 🔐 User Validation
    existing_user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found. Please register before generating a quiz.")
    
    if current_user != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    # 🧠 Fetch the quiz
    quiz = unit_quizzes.find_one({"_id": ObjectId(quiz_id)})
    if not quiz or quiz.get("user_id") != current_user:
        raise HTTPException(status_code=403, detail="Unauthorized or quiz not found")

    questions_lookup = {q["question_text"]: q for q in quiz["questions"]}
    graded = []
    correct_count = 0

    # 📝 Grade responses
    for r in responses:
        q_text = r.question_text
        selected = r.selected_answer
        question = questions_lookup[q_text]

        correct_label = question["correct_answer"]  # already A–E
        is_correct = selected == correct_label

        if is_correct:
            correct_count += 1

        graded.append({
            "question_text": q_text,
            "selected_answer": selected,
            "correct_answer": correct_label,
            "is_correct": is_correct
        })

    # 💾 Store result
    unit_quiz_responses.insert_one({
        "user_id": current_user,
        "quiz_id": quiz_id,
        "unit_name": quiz["unit_name"],
        "responses": graded,
        "submitted_at": datetime.utcnow(),
        "score": correct_count
    })

    return {
        "message": "Quiz submitted successfully!",
        "score": correct_count,
        "total_questions": len(graded),
        "responses": graded
    }

@router.get("/unit_quiz/status/{user_id}")
def get_unit_quiz_status(user_id: str, current_user: str = Depends(get_current_user)):
    """
    Returns all quiz attempts per unit the user has completed.
    """
    existing_user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found.")
        
    if current_user != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    
    attempts = unit_quiz_responses.find({"user_id": current_user}).sort("submitted_at", 1)

    unit_attempts = {}
    for a in attempts:
        unit_name = a["unit_name"]
        if unit_name not in unit_attempts:
            unit_attempts[unit_name] = []
        unit_attempts[unit_name].append({
            "quiz_id": a["quiz_id"],
            "submitted_at": a["submitted_at"],
            "score": a["score"],
            "total_questions": len(a["responses"])
        })

    return unit_attempts

# Route to Get Quiz Results of a particular user
@router.get("/unit_quiz/results/{quiz_id}")
def get_unit_quiz_results(quiz_id: str, current_user: str = Depends(get_current_user)):
    attempt = unit_quiz_responses.find_one({
        "quiz_id": quiz_id,
        "user_id": current_user
    })

    if not attempt:
        raise HTTPException(status_code=404, detail="No attempt found.")

    quiz = unit_quizzes.find_one({
        "_id": ObjectId(quiz_id),
        "user_id": current_user
    })

    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found.")

    # Map each question text to its full data
    question_map = {q["question_text"]: q for q in quiz["questions"]}

    enriched_responses = []

    for r in attempt["responses"]:
        q_text = r["question_text"]
        q_data = question_map.get(q_text, {})
        is_correct = r["is_correct"]

        enriched_responses.append({
            "question_text": q_text,
            "options": q_data.get("options", {}),
            "selected_answer": r["selected_answer"],
            "correct_answer": r["correct_answer"],
            "is_correct": is_correct
        })

    total_questions = len(enriched_responses)

    return {
        "quiz_id": attempt["quiz_id"],
        "unit_name": attempt["unit_name"],
        "submitted_at": attempt["submitted_at"],
        "correct_count": attempt["score"],
        "total_questions": total_questions,
        "responses": enriched_responses
    }

