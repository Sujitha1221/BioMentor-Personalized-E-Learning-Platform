import requests
import logging
import faiss
import numpy as np
import pandas as pd
import time
import os
import textwrap
from dotenv import load_dotenv
from utils.text_extraction import extract_mcqs
from utils.quiz_generation_methods import (
    assign_difficulty_parameter,
    assign_discrimination_parameter,
    retrieve_context_questions,
    is_similar_to_same_quiz_questions,
    is_similar_to_past_quiz_questions,
    is_duplicate_faiss,
    clean_correct_answer,
)
from routes.response_routes import estimate_student_ability
from utils.model_loader import embedding_model, llm
from sklearn.metrics.pairwise import cosine_similarity
from utils.verification import verify_mcq_with_llm

load_dotenv()

# Load FAISS index and dataset
index = faiss.read_index("dataset/question_embeddings.index")
embeddings_matrix = np.load("dataset/question_embeddings.npy")
dataset = pd.read_csv("dataset/question_dataset_with_clusters.csv")

def build_llama2_chat_prompt(instruction: str) -> str:
    return f"<s>[INST] {instruction.strip()} [/INST]"

mcq_cache = {}

# Method to generate MCQs with unique context
def generate_mcq(difficulty, user_id, max_retries=3, existing_questions=None):
    """Generates up to 3 unique MCQs in one API call and returns a list of valid MCQs."""
    retries = 0
    batch_generated_questions = set()
    valid_mcqs = []
    logging.info(f"Attempting to generate MCQs for difficulty: {difficulty}")

    if existing_questions is None:
        existing_questions = set()

    while retries < max_retries and len(valid_mcqs) < 3:
        try:
            #  Check if dataset is empty before sampling
            if dataset.empty:
                logging.error("ERROR: Dataset is empty. Cannot generate MCQ.")
                return []

            sampled_question = dataset.groupby("Cluster").sample(1)

            if sampled_question.empty:
                logging.error("ERROR: No questions available in dataset. Retrying...")
                retries += 1
                continue

            random_question = sampled_question.iloc[0]["Question Text"]
            context_questions = retrieve_context_questions(random_question, top_k=3)

            # Construct context-based prompt
            context_list = (
                [
                    f"- {textwrap.shorten(row['Question Text'], width=250, placeholder='...')} (Correct Answer: {row['Correct Answer']})"
                    for _, row in context_questions.iterrows()                    
                ]
                if not context_questions.empty
                else []
            )

            remaining = 3 - len(valid_mcqs)

            instruction = f"""
            Generate {remaining} **{difficulty}** level multiple-choice biology question{'s' if remaining > 1 else ''}.

            Each question must follow this format:

            Question 1: <Insert your question>
            A) <Option A>
            B) <Option B>
            C) <Option C>
            D) <Option D>
            E) <Option E>
            Correct Answer: <A/B/C/D/E>

            Do not include explanations, numbering, answer keys, or extra text.
            """

            #  Add context if available
            if context_list:
                context_block = "\n".join(context_list)
                prompt = f"""
                Generate a {difficulty}** level MCQ that is **different** from these:

                {context_block}

                **Follow This Format exactly:**
                {instruction.strip()}
                """
            prompt = build_llama2_chat_prompt(instruction)

            #  Send API request (Improved Error Handling)
            try:
                # Calculate prompt token length
                prompt_tokens = len(llm.tokenize(prompt.encode("utf-8")))
                max_total_tokens = 2048
                adjusted_max_tokens = min(768, max_total_tokens - prompt_tokens - 10)  # Ensure room to generate

                if adjusted_max_tokens <= 0:
                    logging.error("🚫 Prompt too long! Skipping generation.")
                    retries += 1
                    continue

                output = llm(prompt, max_tokens=adjusted_max_tokens, temperature=0.8, top_p=0.95)
                if "choices" not in output or not output["choices"]:
                    logging.error("⚠ Model output missing 'choices'. Full output: %s", output)
                    retries += 1
                    continue

                raw_output = output["choices"][0]["text"]
                logging.warning(f"⚠ RAW LOCAL MODEL RESPONSE: {raw_output}")

            except (requests.exceptions.RequestException, ValueError) as e:
                logging.error(f"⚠ Local model error: {e}")
                retries += 1
                time.sleep(1)
                continue

            extracted_mcqs = extract_mcqs(prompt, raw_output)

            if not extracted_mcqs:
                retries += 1
                logging.warning("⚠ No valid MCQs extracted. Retrying...")
                continue

            for question_data in extracted_mcqs:
                question_text = question_data.get("question", "").strip()
                # Duplicate checks
                if (
                    not question_text
                    or is_duplicate_faiss(question_text, index, 0.85)
                    or is_similar_to_same_quiz_questions(
                        question_text, batch_generated_questions, threshold=0.85
                    )
                    or question_text in batch_generated_questions
                    or question_text in existing_questions
                ):
                    continue

                options = question_data.get("options", {})
                correct_letters = clean_correct_answer(
                    question_data.get("correct_answer", "")
                )
                question_data["correct_answer"] = ", ".join(
                    correct_letters
                )  # For consistent formatting

                # Validation checks
                if any(
                    [
                        "error" in question_data,
                        "Question" in question_text,
                        "<Insert your question>" in question_text,
                        "Generate a" in question_text,
                        len(options) != 5,
                        any(not opt.strip() for opt in options.values()),
                        len(set(options.values())) < 5,
                        not correct_letters,
                        any(letter not in options for letter in correct_letters),
                    ]
                ):
                    continue

                #  Add difficulty level
                question_data["difficulty"] = difficulty

                #  Assign difficulty parameters
                question_data["b"] = assign_difficulty_parameter(user_id, difficulty)
                question_data["a"] = assign_discrimination_parameter()
                question_data["c"] = 0.2

                claimed_answer = correct_letters[0] if correct_letters else None

                # Perform answer verification
                is_correct, verified, claimed = verify_mcq_with_llm(
                    question_data["question"], options, claimed_answer
                )

                question_data["claimed_answer"] = (
                    claimed  # Store original generated answer
                )

                if is_correct is False and verified in options:
                    question_data["correct_answer"] = verified
                    question_data["verified_answer"] = verified
                    question_data["is_verified"] = True
                elif is_correct is True:
                    question_data["correct_answer"] = claimed
                    question_data["verified_answer"] = claimed
                    question_data["is_verified"] = True
                else:
                    question_data["verified_answer"] = None
                    question_data["correct_answer"] = claimed
                    question_data["is_verified"] = False

                #  Store in FAISS
                new_vector = embedding_model.encode([question_text]).astype(np.float32)
                index.add(new_vector)

                batch_generated_questions.add(question_text)
                valid_mcqs.append(question_data)

                if len(valid_mcqs) >= 3:
                    break

            if len(valid_mcqs) < 3:
                retries += 1
                logging.warning(
                    f"⚠ Still need {3 - len(valid_mcqs)} MCQs. Retrying... ({retries}/{max_retries})"
                )

        except Exception as e:
            logging.error(f"⚠ Unexpected Error: {e}")
            retries += 1

    return valid_mcqs


def generate_mcq_based_on_performance(
    user_id, difficulty, max_retries=5, existing_questions=None, past_embeddings=None
):
    """Generate up to 3 MCQs based on user's performance, minimizing retries by accepting partial results."""
    retries = 0
    batch_generated_questions = set()
    valid_mcqs = []
    existing_questions = existing_questions or set()

    theta = estimate_student_ability(user_id) or 0.0

    while retries < max_retries and len(valid_mcqs) < 3:
        try:
            if dataset.empty:
                logging.error("Dataset is empty. Cannot generate MCQs.")
                return valid_mcqs

            sampled_question = dataset.groupby("Cluster").sample(1)

            if sampled_question.empty:
                logging.error("ERROR: No questions available in dataset. Retrying...")
                retries += 1
                continue

            random_question = sampled_question.iloc[0]["Question Text"]
            context_questions = retrieve_context_questions(random_question, top_k=3)

            context_list = (
                [
                    f"- {textwrap.shorten(row['Question Text'], width=250, placeholder='...')} (Correct Answer: {row['Correct Answer']})"
                    for _, row in context_questions.iterrows()
                ]
                if not context_questions.empty
                else []
            )

            remaining = 3 - len(valid_mcqs)
            instruction = f"""
            Generate {remaining} **{difficulty}** level multiple-choice biology question{'s' if remaining > 1 else ''}.
            
            **User's Estimated Ability Level (IRT Theta):** {theta}
            
            Each question must follow this format:

            Question 1: <Insert your question>
            A) <Option A>
            B) <Option B>
            C) <Option C>
            D) <Option D>
            E) <Option E>
            Correct Answer: <A/B/C/D/E>

            Do not include explanations, numbering, answer keys, or extra text.
            """

            if context_list:
                context_block = "\n".join(context_list)
                instruction = f"""
                Generate a **{difficulty}** level MCQ that is **different** from these:

                {context_block}

                **Follow This Format exactly:**
                {instruction.strip()}
                """
            prompt = build_llama2_chat_prompt(instruction)
            # Calculate prompt token length
            prompt_tokens = len(llm.tokenize(prompt.encode("utf-8")))
            max_total_tokens = 2048
            adjusted_max_tokens = min(768, max_total_tokens - prompt_tokens - 10)  # Ensure room to generate

            if adjusted_max_tokens <= 0:
                logging.error("🚫 Prompt too long! Skipping generation.")
                retries += 1
                continue

            output = llm(prompt, max_tokens=adjusted_max_tokens, temperature=0.8, top_p=0.95)
            if "choices" not in output or not output["choices"]:
                logging.error("⚠ Model output missing 'choices'. Full output: %s", output)
                retries += 1
                continue

            raw_output = output["choices"][0]["text"]
            logging.warning(f"⚠ RAW LOCAL MODEL RESPONSE: {raw_output}")

            extracted_mcqs = extract_mcqs(prompt, raw_output)

            for mcq in extracted_mcqs:
                question = mcq.get("question", "").strip()
                options = mcq.get("options", {})
                correct_letters = clean_correct_answer(mcq.get("correct_answer", ""))
                claimed_answer = correct_letters[0] if correct_letters else None
                mcq["correct_answer"] = ", ".join(correct_letters)
                # Verification before validation
                is_correct, verified, claimed = verify_mcq_with_llm(
                    question, options, claimed_answer
                )

                # Always store the claimed answer from the model
                mcq["claimed_answer"] = claimed

                if is_correct is False and verified in options:
                    mcq["correct_answer"] = verified  # For scoring
                    mcq["verified_answer"] = (
                        verified  # To show user the corrected value
                    )
                    mcq["is_verified"] = True
                elif is_correct is True:
                    mcq["correct_answer"] = claimed  # Model got it right
                    mcq["verified_answer"] = claimed
                    mcq["is_verified"] = True
                else:
                    mcq["correct_answer"] = claimed  # Fallback to original
                    mcq["verified_answer"] = None
                    mcq["is_verified"] = False

                if any(
                    [
                        is_similar_to_past_quiz_questions(
                            question, user_id, threshold=0.65
                        ),
                        not question,
                        len(options) != 5,
                        any(not v.strip() for v in options.values()),
                        len(set(options.values())) < 5,
                        not correct_letters,
                        any(c not in options for c in correct_letters),
                        is_duplicate_faiss(question, index, 0.85),
                        is_similar_to_same_quiz_questions(
                            question, batch_generated_questions, threshold=0.85
                        ),
                        question in batch_generated_questions,
                        question in existing_questions,
                        "error" in question,
                        "Question" in question,
                        "<Insert your question>" in question,
                        "Generate a" in question,
                    ]
                ):
                    continue

                if past_embeddings is not None:
                    new_vec = embedding_model.encode([question]).astype(np.float32)
                    similarities = cosine_similarity(new_vec, past_embeddings)[0]
                    if max(similarities) >= 0.65:
                        logging.warning(
                            f"🚫 Too similar to past quiz questions (cos sim ≥ 0.65): {question}"
                        )
                        continue

                mcq.update(
                    {
                        "difficulty": difficulty,
                        "b": assign_difficulty_parameter(user_id, difficulty),
                        "a": assign_discrimination_parameter(),
                        "c": 0.2,
                    }
                )

                new_vector = embedding_model.encode([question]).astype(np.float32)
                index.add(new_vector)
                valid_mcqs.append(mcq)
                batch_generated_questions.add(question)

                if len(valid_mcqs) >= 3:
                    break

            if len(valid_mcqs) < 3:
                retries += 1
                logging.warning(
                    f"\u26a0 Still need {3 - len(valid_mcqs)} MCQs. Retrying... ({retries}/{max_retries})"
                )

        except Exception as e:
            logging.error(f"\u26a0 Error in MCQ generation: {e}")
            retries += 1
            time.sleep(1)  # slight delay between retries

    return valid_mcqs
