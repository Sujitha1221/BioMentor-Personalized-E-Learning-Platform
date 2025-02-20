import logging
from datetime import datetime
from pymongo import MongoClient
from evaluate_answers import save_evaluation, evaluate_answer_hybrid
import pandas as pd
import random

# Set up logging
logging.basicConfig(level=logging.INFO)

# MongoDB connection
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

# Global Database Connection
db = get_db()
collection = db["student_assigned_questions"]

# Load CSV **Globally**
FILE_PATH = "Notes/cleaned_question_and_answer.csv"
try:
    df = pd.read_csv(FILE_PATH)
    # Ensure required columns exist
    if not {"Question", "Answer", "Type"}.issubset(df.columns):
        raise ValueError("Dataset must contain 'Question', 'Answer', and 'Type' columns")

    logging.info("CSV file loaded successfully.")

except Exception as e:
    logging.error(f"Error loading CSV file: {e}", exc_info=True)
    df = None  # Set df to None in case of failure

# Select One Random Structured & Essay Question
def get_one_sample_question():
    """
    Selects one random structured and one random essay-type question with answers from a DataFrame.
    """
    try:
        if df is None:
            raise ValueError("Dataset is not loaded. Please check the CSV file.")

        # Select one random structured question
        structured_question = df[df["Type"] == "Structure"].sample(n=1, random_state=random.randint(1, 10000))

        # Select one random essay question
        essay_question = df[df["Type"] == "Essay"].sample(n=1, random_state=random.randint(1, 10000))

        # Create a dictionary with the selected questions and answers
        selected_questions = {
            "Structured_Question": {
                "Question": structured_question.iloc[0]["Question"],
                "Answer": structured_question.iloc[0]["Answer"]
            },
            "Essay_Question": {
                "Question": essay_question.iloc[0]["Question"],
                "Answer": essay_question.iloc[0]["Answer"]
            }
        }

        return selected_questions

    except Exception as e:
        logging.error(f"Error selecting sample questions: {e}", exc_info=True)
        return None

# Select Questions Per Student
def select_questions_per_student(student_id):
    """
    Select one structured and one essay question per student,
    store them in MongoDB, and return the assigned questions.
    """
    # Get one structured and one essay question
    selected_questions = get_one_sample_question()  # ✅ No need to pass df
    if not selected_questions:
        return None
    
    selected_questions["Student_ID"] = student_id
    selected_questions["Assigned_Date"] = datetime.utcnow()

    # Insert into MongoDB
    collection.insert_one(selected_questions)

    logging.info(f"Questions assigned to Student ID {student_id} and stored in MongoDB.")
    return selected_questions

def get_questions_by_student_id(student_id):
    """
    Fetches the assigned structured and essay questions for a given student ID from MongoDB.
    """
    try:
        # Query MongoDB to find the assigned questions for the student
        record = collection.find_one({"Student_ID": student_id}, {"_id": 0})

        if not record:
            return {"error": f"No questions found for Student ID {student_id}"}

        # Check if the required fields exist
        if "Structured_Question" not in record or "Essay_Question" not in record:
            return {"error": f"No valid questions found for Student ID {student_id}"}

        return {
            "Structured_Question": record["Structured_Question"],
            "Essay_Question": record["Essay_Question"],
            "Assigned_Date": record.get("Assigned_Date")
        }

    except Exception as e:
        logging.error(f"Error fetching questions for Student ID {student_id}: {e}", exc_info=True)
        return {"error": "Error retrieving questions"}

def compare_with_passpaper_answer (student_id, question, user_answer, question_type):
    """
    Evaluates the user's answer against the assigned pass paper answer based on the question type.
    """
    logging.info(f"Evaluating user's answer. Question: '{question}', Question Type: '{question_type}'")
    try:
        # Query MongoDB to find the assigned questions for the student
        record = collection.find_one({"Student_ID": student_id}, {"_id": 0})

        if not record:
            return {"error": f"No questions found for Student ID {student_id}"}

        # Fetch the correct model answer based on the question type
        if question_type.lower() == "structured":
            pass_paper_answer = record.get("Structured_Question", {}).get("Answer", None)
        elif question_type.lower() == "essay":
            pass_paper_answer = record.get("Essay_Question", {}).get("Answer", None)
        else:
            return {"error": f"Invalid question type: {question_type}"}

        if not pass_paper_answer:
            return {"error": f"Pass paper answer not found for {question_type} question."}

        # Evaluate the user's answer against the saved answer
        logging.info("Evaluating user's answer against the pass paper answer...")
        result = evaluate_answer_hybrid(user_answer, pass_paper_answer)
        logging.info("Evaluation completed successfully.")

        # Save evaluation result
        save_evaluation(student_id, question, question_type, user_answer, pass_paper_answer, result)

        return {
            "student_id": student_id,
            "question": question,
            "question_type": question_type,
            "user_answer": user_answer,
            "model_answer": pass_paper_answer,
            "evaluation_result": result
        }
    except Exception as e:
        logging.error(f"Error occurred while evaluating user's answer: {e}", exc_info=True)
        return {"error": "Error evaluating answer"}


# Run Tests
if __name__ == "__main__":
    STUDENT_ID = "1234"  # Example Student ID

    assigned_questions = compare_with_passpaper_answer(STUDENT_ID, "Indicate the type of fertilization in the Earthworm", "Mitochondria.", "structured")
    print(assigned_questions)
