# from fastapi import APIRouter, HTTPException
# from database.database import conn, cursor
# from typing import List
# from pydantic import BaseModel

# router = APIRouter()

# # Request model for quiz submission
# class QuizResponse(BaseModel):
#     question_id: int
#     selected_answer: str
#     time_taken: int  # Time in seconds

# @router.post("/submit_quiz/{user_id}/{quiz_id}")
# def submit_quiz(user_id: int, quiz_id: str, responses: List[QuizResponse]):
#     try:
#         correct_count = 0
#         topic_performance = {}
#         difficulty_performance = {"easy": [], "medium": [], "hard": []}

#         for response in responses:
#             question_id = response.question_id
#             selected_answer = response.selected_answer
#             time_taken = response.time_taken

#             # Get correct answer, topic, and difficulty from database
#             cursor.execute("SELECT correct_answer, topic, difficulty FROM quiz_questions WHERE id = %s", (question_id,))
#             question_record = cursor.fetchone()

#             if not question_record:
#                 raise HTTPException(status_code=400, detail=f"Question ID {question_id} not found.")

#             correct_answer, topic, difficulty = question_record
#             is_correct = selected_answer == correct_answer

#             if is_correct:
#                 correct_count += 1

#             # Track topic performance
#             if topic not in topic_performance:
#                 topic_performance[topic] = {"correct": 0, "total": 0}
#             topic_performance[topic]["total"] += 1
#             if is_correct:
#                 topic_performance[topic]["correct"] += 1

#             # Track difficulty performance
#             difficulty_performance[difficulty].append(is_correct)

#             # Store user response in the database
#             cursor.execute("""
#                 INSERT INTO user_responses (user_id, quiz_id, question_id, selected_answer, is_correct, time_taken, topic, difficulty)
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#             """, (user_id, quiz_id, question_id, selected_answer, is_correct, time_taken, topic, difficulty))

#         conn.commit()

#         # Calculate topic-wise accuracy
#         topic_accuracy = {
#             topic: round((data["correct"] / data["total"]) * 100, 2) for topic, data in topic_performance.items()
#         }

#         # Calculate difficulty-wise accuracy
#         difficulty_accuracy = {
#             diff: round((sum(correct) / len(correct)) * 100, 2) if correct else 0
#             for diff, correct in difficulty_performance.items()
#         }

#         return {
#             "message": "Quiz submitted successfully!",
#             "total_correct": correct_count,
#             "score": f"{correct_count}/{len(responses)}",
#             "topic_accuracy": topic_accuracy,
#             "difficulty_accuracy": difficulty_accuracy
#         }
    
#     except Exception as e:
#         conn.rollback()
#         raise HTTPException(status_code=500, detail=str(e))
