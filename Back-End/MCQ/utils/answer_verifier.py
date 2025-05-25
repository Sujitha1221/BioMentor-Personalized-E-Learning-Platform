import time
import logging
from database.database import quizzes_collection
from utils.verification import verify_mcq_with_llm
import os
import google.generativeai as genai

# Load the Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure the Gemini SDK
genai.configure(api_key=GEMINI_API_KEY)

# Ensure logging is configured
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

def verify_quiz_answers_async(quiz_id):
    quiz = quizzes_collection.find_one({"quiz_id": quiz_id})
    if not quiz:
        logging.error(f"[VERIFIER] ❌ Quiz {quiz_id} not found.")
        return

    logging.info(f"[VERIFIER] 🔍 Starting verification for Quiz {quiz_id}")
    updated = False

    for i, q in enumerate(quiz["questions"]):
        if q.get("is_verified"):
            logging.info(f"[VERIFIER] Q{i+1}: ✅ Already verified. Skipping.")
            continue

        question_text = q["question_text"]
        options = {
            "A": q.get("option1", ""),
            "B": q.get("option2", ""),
            "C": q.get("option3", ""),
            "D": q.get("option4", ""),
            "E": q.get("option5", ""),
        }
        claimed = q.get("correct_answer", "N/A")

        logging.info(f"[VERIFIER] Q{i+1}: Verifying '{question_text[:60]}...' Claimed: {claimed}")

        is_correct, verified, claimed_answer = verify_mcq_with_llm(question_text, options, claimed)

        # Always save the claimed answer
        q["claimed_answer"] = claimed_answer

        if is_correct is False and verified in options:
            logging.warning(f"[VERIFIER] Q{i+1}: ❌ Incorrect → Fixing answer: {claimed_answer} → {verified}")
            q["correct_answer"] = verified
            q["verified_answer"] = verified
        else:
            logging.info(f"[VERIFIER] Q{i+1}: ✅ Verified as correct.")
            q["correct_answer"] = claimed_answer
            q["verified_answer"] = claimed_answer

        q["is_verified"] = True
        updated = True

        # ✅ Delay to stay under Gemini free-tier limit (15 requests/min)
        if i < len(quiz["questions"]) - 1:
            time.sleep(4.1)

    if updated:
        quizzes_collection.update_one(
            {"quiz_id": quiz_id}, {"$set": {"questions": quiz["questions"]}}
        )
        logging.info(f"[VERIFIER] ✅ Quiz {quiz_id} verification completed and saved.")
    else:
        logging.info(f"[VERIFIER] 💤 No changes made. All questions were already verified.")


def generate_mcq_with_gemini(prompt: str) -> str:
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        return response.text.strip()
    except Exception as e:
        raise RuntimeError(f"Gemini SDK failed: {e}")