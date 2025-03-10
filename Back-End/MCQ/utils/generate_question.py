import requests
import logging
import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from utils.quiz_generation_methods import assign_difficulty_parameter, assign_discrimination_parameter, is_question_too_similar, retrieve_context_questions
from routes.response_routes import estimate_student_ability

# Load Sentence Transformer model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Load FAISS index and dataset
index = faiss.read_index("dataset/question_embeddings.index")
embeddings_matrix = np.load("dataset/question_embeddings.npy")
dataset = pd.read_csv("dataset/question_dataset_with_clusters.csv")

# Google Colab API Endpoint
COLAB_API_URL = "https://fc8d-34-125-70-103.ngrok-free.app/generate_mcq"

# Method to generate MCQs with unique context
def generate_mcq(difficulty, user_id, max_retries=3):  # 🔥 Reduced retries to 3
    """Generates an MCQ while ensuring uniqueness via FAISS and diverse context retrieval."""
    retries = 0
    logging.info(f"🎯 Attempting to generate an MCQ for difficulty: {difficulty}")

    while retries < max_retries:
        try:
            # ✅ Check if dataset is empty before sampling
            if dataset.empty:
                logging.error("🔥 ERROR: Dataset is empty. Cannot generate MCQ.")
                return None
            
            sampled_question = dataset.sample(1)

            if sampled_question.empty:
                logging.error("🔥 ERROR: No questions available in dataset. Retrying...")
                retries += 1
                continue  

            random_question = sampled_question.iloc[0]["Question Text"]
            context_questions = retrieve_context_questions(random_question, top_k=3)

            # ✅ Construct context-based prompt
            context_list = [
                f"- {row['Question Text']} (Correct Answer: {row['Correct Answer']})"
                for _, row in context_questions.iterrows()
            ] if not context_questions.empty else []

            prompt = f"""
            Generate a **{difficulty}** level multiple-choice biology question.

            **Requirements:**
            - Must be a completely new and unique question.
            - Must contain exactly **5 unique answer choices** labeled **A-E**.
            - Must explicitly state the correct answer.
            - The correct answer must be **one of the provided choices**.

            **Format:**
            ```
            Question: <Generated Question>
            A) <Option A>
            B) <Option B>
            C) <Option C>
            D) <Option D>
            E) <Option E>
            Correct Answer: <A/B/C/D/E>
            ```
            """

            # ✅ Add context if available
            if context_list:
                prompt = f"""
                Generate a **{difficulty}** level MCQ that is **different** from these:

                {''.join(context_list)}

                **Follow This Format:**
                {prompt}
                """

            # ✅ Send API request (Improved Error Handling)
            try:
                response = requests.post(COLAB_API_URL, json={"prompt": prompt}, timeout=30)
                response.raise_for_status()  # 🔥 Handle HTTP errors
                data = response.json()
            except (requests.exceptions.RequestException, ValueError) as e:
                logging.error(f"⚠ API Error: {e}")
                retries += 1
                continue

            # ✅ Debug: Log API response
            logging.warning(f"⚠ RAW API RESPONSE: {data}")

            # ✅ Ensure response is correctly formatted
            if not isinstance(data, dict) or "mcq" not in data:
                logging.error(f"🔥 ERROR: Invalid API response format. Retrying...")
                retries += 1
                continue

            question_data = data["mcq"]
            
            # ✅ Handle API errors in response
            if "error" in question_data:
                logging.warning(f"⚠ MCQ API Error: {question_data['error']}. Retrying...")
                retries += 1
                continue

            # ✅ Ensure the question exists and isn't a placeholder
            question_text = question_data.get("question", "").strip()
            if not question_text or "<Generated Question>" in question_text:
                logging.warning(f"⚠ Malformed MCQ detected: {question_data}. Retrying...")
                retries += 1
                continue

            # ✅ Ensure answer choices are unique
            options = question_data.get("options", {})
            
            if any("<Option" in opt for opt in options.values()):
                logging.warning(f"⚠ Placeholder detected in options: {options}. Retrying...")
                retries += 1
                continue 
            
            if len(set(options.values())) < 5:  # 🔥 Check for duplicate answers
                logging.warning(f"⚠ Duplicate answer choices detected: {options}")
                retries += 1
                continue  

            # ✅ Ensure correct answer exists and is valid
            correct_answer = question_data.get("correct_answer", "").strip()
            if correct_answer not in ["A", "B", "C", "D", "E"] or options.get(correct_answer, "") not in options.values():
                logging.warning(f"⚠ Incorrect correct answer: {correct_answer} not in {options}")
                retries += 1
                continue  

            # ✅ Ensure question is unique (Avoid FAISS similarity failures)
            if is_question_too_similar(question_text):
                logging.warning(f"⚠ Too Similar: {question_text}")
                retries += 1
                continue  

            # ✅ Add difficulty level
            question_data["difficulty"] = difficulty

            # ✅ Assign difficulty parameters
            question_data["b"] = assign_difficulty_parameter(user_id, difficulty)
            question_data["a"] = assign_discrimination_parameter()
            question_data["c"] = 0.2  

            # ✅ Store in FAISS
            new_vector = embedding_model.encode([question_text]).astype(np.float32)
            index.add(new_vector)

            logging.info(f"✅ Successfully generated MCQ: {question_text}")
            return question_data

        except Exception as e:
            logging.error(f"⚠ Unexpected Error: {e}")
            retries += 1

    logging.error("❌ Failed to generate a unique MCQ after multiple attempts.")
    return None  # 🔥 Return None instead of an error


def generate_mcq_based_on_performance(user_id, difficulty, max_retries=5):
    """Generates a new MCQ dynamically based on user's past performance and assigns IRT parameters using ability level."""
    retries = 0
    logging.info(f"🎯 Attempting to generate an MCQ for difficulty: {difficulty}")

    while retries < max_retries:
        # ✅ Fetch user ability
        theta = estimate_student_ability(user_id) or 0.0  # Default if None
        try:
            # ✅ Check if dataset is empty before sampling
            if dataset.empty:
                logging.error("🔥 ERROR: Dataset is empty. Cannot generate MCQ.")
                return None
            
            sampled_question = dataset.sample(1)

            if sampled_question.empty:
                logging.error("🔥 ERROR: No questions available in dataset. Retrying...")
                retries += 1
                continue  

            random_question = sampled_question.iloc[0]["Question Text"]
            context_questions = retrieve_context_questions(random_question, top_k=3)

            # ✅ Construct context-based prompt
            context_list = [
                f"- {row['Question Text']} (Correct Answer: {row['Correct Answer']})"
                for _, row in context_questions.iterrows()
            ] if not context_questions.empty else [] 
           
            prompt = f"""
            Generate a **{difficulty}** level multiple-choice biology question.
        
            **User's Estimated Ability Level (IRT Theta):** {theta}
        
            **Requirements:**
            - Must be a completely new and unique question.
            - Must contain exactly **5 unique answer choices** labeled **A-E**.
            - Must explicitly state the correct answer.
            - The correct answer must be **one of the provided choices**.

            **Format:**
        
            Question: <Generated Question>
            A) <Option A>
            B) <Option B>
            C) <Option C>
            D) <Option D>
            E) <Option E>
            Correct Answer: <A/B/C/D/E>

            """
        
            # ✅ Add context if available
            if context_list:
                prompt = f"""
                Generate a **{difficulty}** level MCQ that is **different** from these:

                {''.join(context_list)}

                **Follow This Format:**
                {prompt}
                """

            try:
                response = requests.post(COLAB_API_URL, json={"prompt": prompt}, timeout=30)
                response.raise_for_status()  # 🔥 Handle HTTP errors
                data = response.json()
            except (requests.exceptions.RequestException, ValueError) as e:
                logging.error(f"⚠ API Error: {e}")
                retries += 1
                continue

            # ✅ Debug: Log API response
            logging.warning(f"⚠ RAW API RESPONSE: {data}")

            # ✅ Ensure response is correctly formatted
            if not isinstance(data, dict) or "mcq" not in data:
                logging.error(f"🔥 ERROR: Invalid API response format. Retrying...")
                retries += 1
                continue

            question_data = data["mcq"]

            # ✅ Handle API errors in response
            if "error" in question_data:
                logging.warning(f"⚠ MCQ API Error: {question_data['error']}. Retrying...")
                retries += 1
                continue

            # ✅ Ensure the question exists and isn't a placeholder
            question_text = question_data.get("question", "").strip()
            if not question_text or "<Generated Question>" in question_text:
                logging.warning(f"⚠ Malformed MCQ detected: {question_data}. Retrying...")
                retries += 1
                continue

            # ✅ Ensure answer choices are unique
            options = question_data.get("options", {})
            
            if any("<Option" in opt for opt in options.values()):
                logging.warning(f"⚠ Placeholder detected in options: {options}. Retrying...")
                retries += 1
                continue 
            
            if len(set(options.values())) < 5:  # 🔥 Check for duplicate answers
                logging.warning(f"⚠ Duplicate answer choices detected: {options}")
                retries += 1
                continue  

            # ✅ Ensure correct answer is valid
            correct_answer = question_data.get("correct_answer", "").strip()
            answer_choices = ["A", "B", "C", "D", "E"]
            if correct_answer not in answer_choices or options.get(correct_answer, "") not in options.values():
                logging.warning(f"⚠ Correct answer mismatch: {correct_answer} not in {options}")
                retries += 1
                continue

            # ✅ Ensure question is unique (Avoid FAISS similarity failures)
            if is_question_too_similar(question_text):
                logging.warning(f"⚠ Too Similar: {question_text}")
                retries += 1
                continue  

            # ✅ Add difficulty to each question
            question_data["difficulty"] = difficulty

            # ✅ Assign IRT parameters dynamically
            question_data["b"] = assign_difficulty_parameter(user_id, difficulty)  # Pass correct user_id
            question_data["a"] = assign_discrimination_parameter()
            question_data["c"] = 0.2  # Fixed guessing parameter

            # ✅ Store in FAISS
            new_vector = embedding_model.encode([question_text]).astype(np.float32)
            index.add(new_vector)
        
            logging.info(f"✅ Successfully generated MCQ: {question_data['question']}")
            return question_data

    # ✅ Handle unexpected errors
        except Exception as e:
            logging.error(f"⚠ Unexpected Error: {e}")
            retries += 1  # ✅ Make sure this line is indented properly

    logging.error("❌ Failed to generate a unique MCQ after multiple attempts.")
    return None  # 🔥 Return None instead of an error

