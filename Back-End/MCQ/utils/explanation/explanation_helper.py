# utils/explanation_helper.py
import logging
from utils.model_loader import llm
from utils.explanation.RAG_biology_helper import RAGBiology
import re
import requests
import os
import google.generativeai as genai

logger = logging.getLogger("explanation_helper")
logger.setLevel(logging.INFO)

rag = RAGBiology()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-1.5-flash")


def extract_answer_from_response(raw_text: str, options: dict) -> str:
    lines = raw_text.splitlines()

    # Match formats like "2. Answer: B" or "Answer: B"
    for line in lines:
        match = re.search(r"\bAnswer\s*[:\-]?\s*([A-E])\b", line, re.IGNORECASE)
        if match:
            letter = match.group(1).upper()
            if letter in options:
                return letter

    # Fallback: line with just a letter
    for line in lines:
        clean = line.strip().upper()
        if clean in options and len(clean) == 1:
            return clean

    return None


def clean_explanation_text(raw_text: str) -> str:
    # Split and clean lines
    lines = raw_text.splitlines()

    # Remove any "Answer: X" line (even numbered like "2. Answer: X")
    cleaned = []
    for line in lines:
        if re.match(
            r"^(\d+\.\s*)?Answer\s*[:\-]?\s*[A-E]\s*$", line.strip(), re.IGNORECASE
        ):
            continue  # skip
        cleaned.append(line)

    # Join and remove repeated 'Explanation:' markers
    text = "\n".join(cleaned)
    explanation_parts = re.split(r"\bExplanation:\s*", text, flags=re.IGNORECASE)

    if len(explanation_parts) > 1:
        return "Explanation: " + explanation_parts[1].strip()
    return text.strip()


def build_prompt_with_context_for_explanation(
    question: str, options: dict, context_list: list
) -> str:
    context = "\n".join([f"- {c}" for c in context_list])
    options_text = "\n".join([f"{k}) {v}" for k, v in options.items()])

    return f"""
You are a biology expert.

Use the following textbook context to answer the question:

Context:
{context}

Question: {question}
Options:
{options_text}

Instructions:
1. Answer with the correct option letter (A–E) on the first line.
2. Then explain in **1–2 short sentences** using the context.
3. Do not include extra details or repeat the question.


Format:
Answer: X
Explanation: ...
"""

def explain_mcq(question: str, options: dict) -> dict:
    logger.info("🔍 Generating explanation using context")
    context = rag.get_context(question, top_k=3, max_total_words=250)
    prompt = build_prompt_with_context_for_explanation(question, options, context)

    response = llm(prompt, max_tokens=400)
    raw_text = response["choices"][0]["text"].strip()

    predicted_answer = extract_answer_from_response(raw_text, options)
    cleaned_explanation = clean_explanation_text(raw_text)

    if not predicted_answer or not is_explanation_valid(cleaned_explanation):
        return fallback_to_gemini(question, options)

    # Gemini reviews the answer + explanation; corrects if necessary
    return review_with_gemini(question, options, predicted_answer, cleaned_explanation)


def verify_answer_by_generation(
    question: str, options: dict, claimed_answer: str
) -> dict:
    logger.info("🔍 Verifying claimed answer by solving the MCQ directly.")

    result = explain_mcq(question, options)
    predicted = result.get("predicted_answer")
    explanation = result.get("explanation")

    if not predicted:
        logger.warning("⚠️ Both local model and fallback failed to extract answer.")
        return {
            "is_correct": False,
            "predicted_answer": None,
            "claimed_answer": claimed_answer.upper(),
            "explanation": explanation or "Model could not determine an answer.",
        }

    is_correct = predicted == claimed_answer.strip().upper()

    return {
        "is_correct": is_correct,
        "predicted_answer": predicted,
        "claimed_answer": claimed_answer.upper(),
        "explanation": explanation,
    }


def fallback_to_gemini(question: str, options: dict) -> dict:
    prompt = (
        f"""You are a biology expert.

Question: {question}
Options:
"""
        + "\n".join([f"{k}) {v}" for k, v in options.items()])
        + """

Instructions:
1. On the first line, write: Answer: X (where X is A–E)
2. On the second line, write a short explanation.
Only return the answer and explanation. No extra text.
"""
    )

    try:
        response = gemini_model.generate_content(prompt)
        gemini_text = response.text.strip()

        predicted = extract_answer_from_response(gemini_text, options)
        explanation = clean_explanation_text(gemini_text)

        return {
            "predicted_answer": predicted,
            "explanation": explanation,
        }

    except Exception as e:
        raise RuntimeError(f"Gemini fallback failed: {e}")


def review_with_gemini(
    question: str, options: dict, predicted_answer: str, explanation: str
) -> dict:
    prompt = f"""
    You are a biology tutor reviewing an AI-generated multiple-choice answer.

    Question: {question}
    Options:
    {chr(10).join([f"{k}) {v}" for k, v in options.items()])}

    AI's Answer: {predicted_answer}
    AI's Explanation: {explanation}

    Instructions:
    1. If the answer and explanation are both correct, just reply with:
    Answer: <same letter>
    Explanation: <same explanation>

    2. If either is wrong or inconsistent, reply with the correct answer and explanation in the same format.

    Only return:
    Answer: X
    Explanation: <corrected explanation>
    No extra comments.
    """

    try:
        response = gemini_model.generate_content(prompt)
        gemini_text = response.text.strip()

        corrected_answer = extract_answer_from_response(gemini_text, options)
        corrected_explanation = clean_explanation_text(gemini_text)

        return {
            "predicted_answer": corrected_answer or predicted_answer,
            "explanation": corrected_explanation or explanation,
        }

    except Exception as e:
        logger.warning(f"⚠️ Gemini review failed: {e}")
        return {
            "predicted_answer": predicted_answer,
            "explanation": explanation,
        }


def is_explanation_valid(explanation: str) -> bool:
    if not explanation:
        return False
    if len(explanation.strip()) < 20:
        return False
    if "i don't know" in explanation.lower():
        return False
    if re.match(r"^Explanation:\s*[\.\-]*$", explanation.strip()):
        return False
    return True

def is_inappropriate(question: str) -> bool:
    banned_keywords = [
        "bomb", "kill", "terrorist", "rape", "nazi", "abuse", "sex", "porn",
        "explosive", "weapon", "murder", "shoot", "drugs", "hack", "curse",
        "fuck", "shit", "bitch", "asshole", "suicide"
    ]
    return any(word in question.lower() for word in banned_keywords)

def is_biology_question(question: str) -> bool:
    prompt = f"""
Decide whether the following question is related to biology.

Question: "{question}"

Instructions:
- Answer only with "Yes" or "No".
- Do not add explanations or reasoning.
"""

    try:
        response = gemini_model.generate_content(prompt)
        result = response.text.strip().lower()
        return result.startswith("yes")
    except Exception as e:
        logger.warning(f"⚠️ Gemini classification failed: {e}")
        return True  # Assume it's valid if check fails
