import google.generativeai as genai
import logging
import os
import time

# Load Gemini API key from env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Set this in your .env

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


def verify_mcq_with_llm(question, options, claimed_answer):
    prompt = f"""Question: {question}
Options:
A) {options.get("A", "")}
B) {options.get("B", "")}
C) {options.get("C", "")}
D) {options.get("D", "")}
E) {options.get("E", "")}
Which option is correct? Just reply with a single letter: A, B, C, D, or E."""

    try:
        response = model.generate_content(prompt)
        prediction = response.text.strip().upper()
        predicted_letter = (
            prediction[0] if prediction and prediction[0] in options else None
        )
        is_correct = predicted_letter == claimed_answer
        return is_correct, predicted_letter, claimed_answer

    except Exception as e:
        error_msg = str(e)
        logging.error(f"[Gemini Verifier] Error: {error_msg}")

        # Check for 429 error and apply backoff
        if "429" in error_msg or "rate limit" in error_msg.lower():
            logging.warning("⚠ Rate limit hit. Retrying after 60 seconds...")
            time.sleep(60)
            try:
                # Retry once
                response = model.generate_content(prompt)
                prediction = response.text.strip().upper()
                predicted_letter = (
                    prediction[0] if prediction and prediction[0] in options else None
                )
                is_correct = predicted_letter == claimed_answer
                return is_correct, predicted_letter, claimed_answer
            except Exception as retry_err:
                logging.error(f"[Gemini Retry] Failed again: {retry_err}")
                return None, None, claimed_answer

        # Fallback if other type of error
        return None, None, claimed_answer
