import os
import faiss
import numpy as np
import pandas as pd
import logging
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
from sentence_transformers import SentenceTransformer

NOTES_CSV_PATH = "Notes/cleaned_Notes.csv"  # Study Notes CSV
FAISS_INDEX_PATH = "DB/cleaned_Notes_faiss_index.bin"  # FAISS Index Storage
MODEL_NAME = 'all-MiniLM-L6-v2'  # Fast & Lightweight SentenceTransformer Model


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

# MongoDB Connection
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

db = get_db()

# Load the notes dataset
def load_notes():
    if not os.path.exists(NOTES_CSV_PATH):
        raise FileNotFoundError(f"Notes file not found: {NOTES_CSV_PATH}")
    return pd.read_csv(NOTES_CSV_PATH)

# Load or create FAISS Index without saving embeddings
def load_or_create_faiss(notes_df):
    model = SentenceTransformer(MODEL_NAME)

    if os.path.exists(FAISS_INDEX_PATH):
        print("Loading existing FAISS index...")
        index = faiss.read_index(FAISS_INDEX_PATH)

        # Check if FAISS has the same number of records as the dataset
        if index.ntotal == len(notes_df):
            print("FAISS index is up-to-date. No need to recompute embeddings.")
            return index

        print("Detected new study materials. Updating FAISS index...")
    else:
        print("Creating new FAISS index...")

    # Convert all study materials into embeddings (only in memory, not saved)
    notes_texts = notes_df["Text Content"].tolist()
    notes_embeddings = model.encode(notes_texts)
    notes_embeddings = np.array(notes_embeddings)

    # Initialize FAISS index (L2 Distance)
    embedding_dim = notes_embeddings.shape[1]
    index = faiss.IndexFlatL2(embedding_dim)
    index.add(notes_embeddings)

    # Save FAISS index (but not embeddings)
    faiss.write_index(index, FAISS_INDEX_PATH)

    print(f"FAISS index updated | {index.ntotal} entries")
    return index

notes_df = load_notes()  
index = load_or_create_faiss(notes_df)  

# Save Evaluation Data
def save_evaluation(student_id, question, question_type, user_answer, model_answer, evaluation_result):
    """
    Save evaluation data to MongoDB.
    """
    try:
        collection = db["evaluations"]
        record = {
            "student_id": student_id,
            "question": question,
            "question_type": question_type,
            "user_answer": user_answer,
            "model_answer": model_answer,
            "evaluation_result": evaluation_result,
            "timestamp": datetime.utcnow()
        }
        collection.insert_one(record)
        logging.info(f"Evaluation data saved for student_id: {student_id}")
    except Exception as e:
        logging.error(f"Error saving evaluation data: {e}", exc_info=True)
        raise

# Retrieve Evaluations for a Student
def get_student_evaluations(student_id):
    """
    Retrieve all evaluations for a specific student.
    """
    try:
        collection = db["evaluations"]
        evaluations = list(collection.find({"student_id": student_id}))
        logging.info(f"Retrieved {len(evaluations)} evaluations for student_id: {student_id}")
        return convert_objectid(evaluations)
    except Exception as e:
        logging.error(f"Error retrieving evaluations for student_id: {student_id}", exc_info=True)
        raise

# Compute Average Scores
def compute_average_scores(student_id):
    """
    Compute average scores for a student.
    """
    evaluations = get_student_evaluations(student_id)
    if not evaluations:
        logging.warning(f"No evaluations found for student_id: {student_id}")
        return {"message": f"No evaluations found for student_id: {student_id}"}

    metrics = ["semantic_score", "tfidf_score", "jaccard_score", "grammar_score"]
    averages = {metric: 0 for metric in metrics}

    for eval in evaluations:
        for metric in metrics:
            averages[metric] += eval["evaluation_result"].get(metric, 0)

    averages = {metric: round(total / len(evaluations), 2) for metric, total in averages.items()}
    logging.info(f"Average scores for student_id {student_id}: {averages}")
    return averages

# Get Score Trends
def get_score_trends(student_id):
    """
    Get score trends for a student as a dictionary.
    """
    evaluations = get_student_evaluations(student_id)
    if not evaluations:
        logging.warning(f"No evaluations found for student_id: {student_id}")
        return {"message": f"No evaluations found for student_id: {student_id}"}

    timestamps = [eval["timestamp"] for eval in evaluations]
    scores = {metric: [] for metric in ["semantic_score", "tfidf_score", "jaccard_score", "grammar_score"]}

    for eval in evaluations:
        for metric in scores.keys():
            scores[metric].append(eval["evaluation_result"].get(metric, 0))

    trends = {
        "timestamps": timestamps,
        "scores": scores
    }

    logging.info(f"Score trends for student_id {student_id}: {trends}")
    return trends

# Group-Level Analysis
def get_group_analysis(student_ids):
    """
    Perform group-level analysis for specific students and return the results as a dictionary.
    """
    try:
        # Ensure student_ids is a list
        if not isinstance(student_ids, list):
            if isinstance(student_ids, str):
                student_ids = [student_ids]  # Convert single string to list
            else:
                raise ValueError("student_ids must be a list or a single string.")

        collection = db["evaluations"]
        
        # Query evaluations for the specified student IDs
        evaluations = list(collection.find({"student_id": {"$in": student_ids}}))

        if not evaluations:
            logging.warning(f"No evaluations found for the given student IDs: {student_ids}")
            return {"message": f"No evaluations found for the given student IDs: {student_ids}"}

        metrics = ["semantic_score", "tfidf_score", "jaccard_score", "grammar_score"]
        averages = {metric: 0 for metric in metrics}

        for eval in evaluations:
            for metric in metrics:
                averages[metric] += eval["evaluation_result"].get(metric, 0)

        num_evaluations = len(evaluations)
        averages = {metric: round(total / num_evaluations, 2) for metric, total in averages.items()}

        # Group analysis details
        analysis_details = {
            "student_ids": student_ids,
            "total_evaluations": num_evaluations,
            "average_scores": averages,
            "evaluations_per_student": {
                student_id: len(list(filter(lambda x: x["student_id"] == student_id, evaluations)))
                for student_id in student_ids
            }
        }

        logging.info(f"Group-level analysis by student IDs: {analysis_details}")
        return analysis_details
    except ValueError as ve:
        logging.error(f"ValueError during group-level analysis: {ve}", exc_info=True)
        return {"message": str(ve)}
    except Exception as e:
        logging.error(f"Error during group-level analysis by student IDs: {e}", exc_info=True)
        return {"message": "An error occurred during group-level analysis."}



# Generate Feedback Report
def generate_feedback_report(student_id):
    """
    Generate a feedback report for a student.
    """
    evaluations = get_student_evaluations(student_id)
    if not evaluations:
        logging.warning(f"No evaluations found for student_id: {student_id}")
        return {"message": f"No evaluations found for student_id: {student_id}"}

    logging.info(f"Generating feedback report for student_id: {student_id}")
    strengths = []
    weaknesses = []
    missing_keywords = set()
    extra_keywords = set()
    grammar_errors = 0

    for eval in evaluations:
        feedback = eval["evaluation_result"].get("feedback", {})
        missing_keywords.update(feedback.get("missing_keywords", []))
        extra_keywords.update(feedback.get("extra_keywords", []))
        grammar_errors += len(feedback.get("grammar_suggestions", []))

        # Strengths and weaknesses
        if eval["evaluation_result"]["final_score"] > 80:
            strengths.append(eval["question"])
        else:
            weaknesses.append(eval["question"])

    report = {
        "strengths": strengths,
        "weaknesses": weaknesses,
        "missing_keywords": list(missing_keywords),
        "extra_keywords": list(extra_keywords),
        "grammar_errors": grammar_errors,
    }

    logging.info(f"Feedback Report for student_id {student_id}: {report}")
    return report

# Generate Adaptive Feedback and Recommendations
def generate_recommendations(student_id):
    """
    Generate adaptive feedback and learning path recommendations based on evaluation data.
    """
    evaluations = get_student_evaluations(student_id)
    if not evaluations:
        logging.warning(f"No evaluations found for student_id: {student_id}")
        return {"message": f"No evaluations found for student_id: {student_id}"}

    logging.info(f"Generating adaptive feedback and recommendations for student_id: {student_id}")
    all_keywords = {"mastered": set(), "weak": set(), "frequent_mistakes": set()}
    learning_path = []
    personalized_exercises = []

    for eval in evaluations:
        feedback = eval["evaluation_result"].get("feedback", {})
        missing_keywords = set(feedback.get("missing_keywords", []))
        extra_keywords = set(feedback.get("extra_keywords", []))
        all_keywords["weak"].update(missing_keywords)
        all_keywords["frequent_mistakes"].update(extra_keywords)

        # Identify mastered keywords as those appearing in none of the weak or frequent mistakes
        all_keywords["mastered"] = all_keywords["mastered"].union(set(eval["question"].lower().split())) - all_keywords["weak"] - all_keywords["frequent_mistakes"]

        # Add learning path suggestions
        if missing_keywords:
            topic = eval["question"].split(" ")[-1]  # Assume topic is the last word in the question
            learning_path.append(f"Review materials on: {topic} - Missing keywords: {', '.join(missing_keywords)}")

        # Generate personalized exercises
        if extra_keywords:
            personalized_exercises.append(f"Create a sentence using: {', '.join(extra_keywords)}")
        else:
            personalized_exercises.append(f"Write a short paragraph explaining the topic: {eval['question']}")

    # Generate recommendations as a dictionary
    recommendations = {
        "learning_path": learning_path,
        "personalized_exercises": personalized_exercises,
        "keyword_mastery": {
            "mastered": list(all_keywords["mastered"]),
            "weak": list(all_keywords["weak"]),
            "frequent_mistakes": list(all_keywords["frequent_mistakes"])
        }
    }

    logging.info(f"Recommendations for student_id {student_id}: {recommendations}")
    return recommendations

def calculate_class_average():
    """
    Calculate the overall class average scores across all students.
    """
    try:
        collection = db["evaluations"]
        all_evaluations = list(collection.find({}))  # Fetch all evaluations

        if not all_evaluations:
            return {
                "semantic_score": 0,
                "tfidf_score": 0,
                "jaccard_score": 0,
                "grammar_score": 0,
                "total_students": 0
            }

        metrics = ["semantic_score", "tfidf_score", "jaccard_score", "grammar_score"]
        total_scores = {metric: 0 for metric in metrics}
        student_scores = {}

        # Iterate through each evaluation and sum scores
        for evaluation in all_evaluations:
            student_id = evaluation["student_id"]
            if student_id not in student_scores:
                student_scores[student_id] = {metric: 0 for metric in metrics}
                student_scores[student_id]["count"] = 0

            for metric in metrics:
                student_scores[student_id][metric] += evaluation["evaluation_result"].get(metric, 0)

            student_scores[student_id]["count"] += 1

        total_students = len(student_scores)

        # Calculate final class-wide averages
        for student_id, scores in student_scores.items():
            for metric in metrics:
                total_scores[metric] += scores[metric] / scores["count"]

        class_average = {metric: round(total / total_students, 2) for metric, total in total_scores.items()}
        class_average["total_students"] = total_students

        logging.info(f"Class average calculated: {class_average}")
        return class_average

    except Exception as e:
        logging.error(f"Error calculating class averages: {e}", exc_info=True)
        return {
            "message": "An error occurred while calculating class averages.",
            "error": str(e)
        }

def get_student_analytic_details(student_id):
    """
    Generate and return all details for a given student_id.
    Includes evaluations, average scores, score trends, feedback report, and recommendations.
    """
    try:
        # Step 1: Retrieve evaluations
        evaluations = get_student_evaluations(student_id)
        if not evaluations:
            return {"message": f"No evaluations found for student_id: {student_id}"}

        # Step 2: Compute average scores
        average_scores = compute_average_scores(student_id)

        # Step 3: Get score trends
        score_trends = get_score_trends(student_id)

        # Step 4: Generate feedback report
        feedback_report = generate_feedback_report(student_id)

        # Step 5: Generate adaptive feedback and recommendations
        recommendations = generate_recommendations(student_id)

        # Perform group-level analysis
        group_averages = get_group_analysis(student_id)

        # Get overall class-wide averages
        class_average = calculate_class_average()

        # Find matched study materials based on weak areas
        model = SentenceTransformer(MODEL_NAME)
        matched_notes = recommend_study_materials(student_id, notes_df, index, model)

        # Combine all details into a single dictionary
        student_details = {
            "student_id": student_id,
            "evaluations": evaluations,
            "average_scores": average_scores,
            "score_trends": score_trends,
            "feedback_report": feedback_report,
            "recommendations": recommendations,
            "group_analysis": group_averages,
            "class_average": class_average,
            "matched_study_materials": matched_notes.to_dict(orient="records"),
        }

        logging.info(f"Generated all details for student_id {student_id}")
        return student_details
    except Exception as e:
        logging.error(f"Error generating details for student_id {student_id}: {e}", exc_info=True)
        return {"message": f"An error occurred while generating details for student_id: {student_id}"}

def convert_objectid(data):
    """
    Recursively convert ObjectId to string in a dictionary or list.
    """
    if isinstance(data, list):
        return [convert_objectid(item) for item in data]
    elif isinstance(data, dict):
        return {key: convert_objectid(value) for key, value in data.items()}
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data
    
# Recommend Study Materials Based on Weak Areas
def recommend_study_materials(student_id, notes_df, index, model, top_k=3):
    """Recommend study materials based on the student's weak areas."""
    feedback_report = generate_feedback_report(student_id)
    if "message" in feedback_report:
        logging.warning(f"No feedback report found for student_id: {student_id}")
        return {"message": f"No feedback report available for student_id: {student_id}"}

    weak_keywords = feedback_report.get("missing_keywords", [])
    if not weak_keywords:
        logging.info(f"No weak keywords found for student_id: {student_id}. No study materials needed.")
        return {"message": f"No weak areas identified for student_id: {student_id}"}

    # Combine weak areas into a single query for semantic search
    query_text = " ".join(weak_keywords)
    query_embedding = model.encode([query_text])

    # Search in FAISS (Find top k matches)
    D, I = index.search(np.array(query_embedding), k=top_k)

    # Retrieve the best study notes
    matched_notes = notes_df.iloc[I[0]]

    return matched_notes


# Example Usage
if __name__ == "__main__":
    evaluations = [
        {
            "student_id": "student123",
            "question": "Explain the process of photosynthesis.",
            "question_type": "structured",
            "user_answer": "Photosynthesis produces glucos using sunligt and waterr.",
            "model_answer": "Photosynthesis is a process where plants use sunlight, water, and carbon dioxide to produce glucose and oxygen.",
            "evaluation_result": {
                "final_score": 85.0,
                "semantic_score": 90.0,
                "tfidf_score": 80.0,
                "jaccard_score": 75.0,
                "grammar_score": 95.0,
                "feedback": {
                    "missing_keywords": ["carbon dioxide"],
                    "extra_keywords": ["glucos", "sunligt", "waterr"],
                    "grammar_suggestions": ["Replace 'glucos' with 'glucose'"]
                }
            }
        },
        {
            "student_id": "student123",
            "question": "What is the importance of water in human life?",
            "question_type": "essay",
            "user_answer": "Water is vital for humans. It helps in hydration, reguation of body temperature, and digestion.",
            "model_answer": "Water is essential for human survival as it regulates body temperature, aids in digestion, removes toxins, and keeps cells hydrated.",
            "evaluation_result": {
                "final_score": 78.0,
                "semantic_score": 85.0,
                "tfidf_score": 70.0,
                "jaccard_score": 60.0,
                "grammar_score": 90.0,
                "feedback": {
                    "missing_keywords": ["toxins", "cells"],
                    "extra_keywords": ["reguation"],
                    "grammar_suggestions": ["Replace 'reguation' with 'regulation'"]
                }
            }
        },
        {
            "student_id": "student123",
            "question": "Define gravity and its role in the solar system.",
            "question_type": "structured",
            "user_answer": "Gravity is a force that pulls objects. It keps planets in orbit.",
            "model_answer": "Gravity is the force of attraction that governs the motion of planets, keeping them in orbit around the sun and causing smaller objects to stay on celestial bodies.",
            "evaluation_result": {
                "final_score": 72.0,
                "semantic_score": 80.0,
                "tfidf_score": 65.0,
                "jaccard_score": 70.0,
                "grammar_score": 85.0,
                "feedback": {
                    "missing_keywords": ["motion", "celestial bodies", "attraction"],
                    "extra_keywords": ["keps"],
                    "grammar_suggestions": ["Replace 'keps' with 'keeps'"]
                }
            }
        }
    ]

    # Save evaluations
    for evaluation in evaluations:
        save_evaluation(
            evaluation["student_id"],
            evaluation["question"],
            evaluation["question_type"],
            evaluation["user_answer"],
            evaluation["model_answer"],
            evaluation["evaluation_result"]
        )

    # Compute averages
    averages = compute_average_scores("student123")
    print("Average Scores:", averages)

    # Get score trends
    score_trends = get_score_trends("student123")
    print("Score Trends:", score_trends)

    # Perform group-level analysis
    group_averages = get_group_analysis()
    print("Group-Level Averages:", group_averages)

    # Generate feedback report
    feedback = generate_feedback_report("student123")
    print("Feedback Report:", feedback)

    recommendations = generate_recommendations("student123")
    print("Adaptive Feedback and Recommendations:", recommendations)
