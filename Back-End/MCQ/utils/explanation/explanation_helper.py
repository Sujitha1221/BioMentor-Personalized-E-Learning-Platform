# utils/explanation_helper.py
import logging
from utils.model_loader import llm
from utils.explanation.RAG_biology_helper import RAGBiology
import re
logger = logging.getLogger("explanation_helper")
logger.setLevel(logging.INFO)
import requests
import os
import google.generativeai as genai

rag = RAGBiology()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

def extract_answer_from_response(raw_text: str, options: dict) -> str:
    # Look only for the first valid "Answer: X" that’s not part of a list or example
    lines = raw_text.splitlines()
    
    for line in lines:
        line_clean = line.strip()
        match = re.match(r"^Answer\s*[:\-]?\s*([A-E])$", line_clean, re.IGNORECASE)
        if match:
            letter = match.group(1).upper()
            if letter in options:
                return letter

    # Fallback: first clean letter on a line by itself
    for line in lines:
        line_clean = line.strip().upper()
        if line_clean in options and len(line_clean) == 1:
            return line_clean

    return None

def clean_explanation_text(raw_text: str) -> str:
    # Split and clean lines
    lines = raw_text.splitlines()
    
    # Remove any "Answer: X" line (even numbered like "2. Answer: X")
    cleaned = []
    for line in lines:
        if re.match(r"^(\d+\.\s*)?Answer\s*[:\-]?\s*[A-E]\s*$", line.strip(), re.IGNORECASE):
            continue  # skip
        cleaned.append(line)

    # Join and remove repeated 'Explanation:' markers
    text = "\n".join(cleaned)
    explanation_parts = re.split(r"\bExplanation:\s*", text, flags=re.IGNORECASE)

    if len(explanation_parts) > 1:
        return "Explanation: " + explanation_parts[1].strip()
    return text.strip()


def build_prompt_with_context_for_explanation(question: str, options: dict, context_list: list) -> str:
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

    logger.debug(f"Prompt:\n{prompt}")
    response = llm(prompt, max_tokens=400)
    raw_text = response["choices"][0]["text"].strip()

    predicted_answer = extract_answer_from_response(raw_text, options)
    cleaned_explanation = clean_explanation_text(raw_text)

    if not predicted_answer or not is_explanation_valid(cleaned_explanation):
        logger.warning("⚠️ Local model failed to extract answer. Falling back to Gemini.")
        return fallback_to_gemini(question, options)

    return {
        "predicted_answer": predicted_answer,
        "explanation": cleaned_explanation,
        "fallback_used": False
    }


def verify_answer_by_generation(question: str, options: dict, claimed_answer: str) -> dict:
    logger.info("🔍 Verifying claimed answer by solving the MCQ directly.")

    result = explain_mcq(question, options)
    predicted = result.get("predicted_answer")
    explanation = result.get("explanation")
    fallback_used = result.get("fallback_used", False)

    if not predicted or not is_explanation_valid(explanation):
        logger.warning("⚠️ Both local model and fallback failed to extract answer.")
        return {
            "is_correct": False,
            "predicted_answer": None,
            "claimed_answer": claimed_answer.upper(),
            "explanation": explanation or "Model could not determine an answer.",
            "fallback_used": fallback_used
        }

    is_correct = predicted == claimed_answer.strip().upper()

    return {
        "is_correct": is_correct,
        "predicted_answer": predicted,
        "claimed_answer": claimed_answer.upper(),
        "explanation": explanation,
        "fallback_used": fallback_used
    }


def fallback_to_gemini(question: str, options: dict) -> dict:
    prompt = f"""You are a biology expert.

Question: {question}
Options:
""" + "\n".join([f"{k}) {v}" for k, v in options.items()]) + """

Instructions:
1. On the first line, write: Answer: X (where X is A–E)
2. On the second line, write a short explanation.
Only return the answer and explanation. No extra text.
"""

    try:
        response = gemini_model.generate_content(prompt)
        gemini_text = response.text.strip()

        predicted = extract_answer_from_response(gemini_text, options)
        explanation = clean_explanation_text(gemini_text)

        return {
            "predicted_answer": predicted,
            "explanation": explanation,
            "fallback_used": True
        }

    except Exception as e:
        raise RuntimeError(f"Gemini fallback failed: {e}")

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

