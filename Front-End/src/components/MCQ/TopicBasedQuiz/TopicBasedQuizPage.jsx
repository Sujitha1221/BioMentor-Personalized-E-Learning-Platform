import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import api from "../../axios/api.js";
import LoadingScreen from "../loadingPage/LoadingScreen";
import SubmitConfirmationModal from "../models/ConfirmationModal.jsx"; // ✅ Import Submit Modal

const TopicBasedQuizPage = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const userId = JSON.parse(localStorage.getItem("user"))?.user_id;
  const { quizId, topicName } = location.state || {};
  const token = localStorage.getItem("token");

  const [quiz, setQuiz] = useState(null);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [showSubmitModal, setShowSubmitModal] = useState(false); // ✅ Modal State
  const [isSubmitting, setIsSubmitting] = useState(false); // ✅ Loading State

  useEffect(() => {
    if (!quizId) {
      navigate("/topic-quizzes"); // Redirect if no quizId is found
      return;
    }
    fetchQuiz();
  }, [quizId]);

  const fetchQuiz = async () => {
    try {
      const response = await api.get(`/topic/topic_quiz/${quizId}`, {
        params: { user_id: userId },
        headers: { Authorization: `Bearer ${token}` },
      });
      setQuiz(response.data);
    } catch (error) {
      console.error("Error fetching quiz:", error);
      navigate("/topic-quizzes"); // Redirect if quiz is unavailable
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerSelect = (answer) => {
    setAnswers((prev) => ({
      ...prev,
      [currentQuestionIndex]: answer,
    }));
  };

  const handleSubmit = async () => {
    setIsSubmitting(true); // ✅ Show Loading Button State
    try {
      const responses = quiz.questions.map((q, index) => ({
        question_text: q.question_text,
        selected_answer: answers[index] || "Not Answered",
      }));
      const requestData = {
        user_id: userId,
        quiz_id: quizId,
        responses: responses,
      };

      await api.post(`/topic/questions/submit`, requestData, {
        headers: { Authorization: `Bearer ${token}` },
      });

      navigate(`/topic_quiz/results`, { state: { quizId, topicName } });
    } catch (error) {
      console.error("Error submitting quiz:", error);
    } finally {
      setIsSubmitting(false); // ✅ Hide Loading Button
    }
  };

  const checkUnansweredQuestions = () => {
    const unanswered = quiz.questions.filter(
      (_, index) => !answers[index]
    ).length;
    return unanswered > 0;
  };

  const confirmSubmit = () => {
    setShowSubmitModal(true);
  };

  if (loading) {
    return <LoadingScreen />;
  }

  const currentQuestion = quiz.questions[currentQuestionIndex];
  const totalQuestions = quiz.questions.length;

  return (
    <div className="min-h-screen mt-0 sm:mt-20 flex bg-gradient-to-br from-gray-100 to-gray-200 text-gray-900 p-5">
      {/* Left: Question Section */}
      <div className="w-3/4 flex flex-col justify-between bg-white p-6 rounded-lg shadow-lg">
        <motion.h1
          className="text-3xl font-extrabold text-indigo-700 text-center mb-6"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          📝 {topicName} Quiz
        </motion.h1>

        {/* Question */}
        <div>
          <h3 className="text-xl font-semibold text-gray-800 mb-4">
            {currentQuestionIndex + 1}. {currentQuestion.question_text}
          </h3>
          <div className="space-y-3">
            {Object.entries(currentQuestion.options).map(([letter, option]) => (
              <button
                key={letter}
                onClick={() => handleAnswerSelect(letter)}
                className={`block w-full px-4 py-2 rounded-lg border transition-all text-left ${
                  answers[currentQuestionIndex] === letter
                    ? "bg-blue-500 text-white"
                    : "bg-gray-200 hover:bg-gray-300"
                }`}
              >
                {letter}. {option}
              </button>
            ))}
          </div>
        </div>

        {/* Navigation Buttons */}
        <div className="flex justify-between mt-4">
          <button
            onClick={() =>
              setCurrentQuestionIndex((prev) => Math.max(prev - 1, 0))
            }
            disabled={currentQuestionIndex === 0}
            className={`px-6 py-3 rounded-lg font-semibold text-lg transition-all ${
              currentQuestionIndex === 0
                ? "bg-gray-300 text-gray-600 cursor-not-allowed"
                : "bg-indigo-500 text-white hover:bg-indigo-700"
            }`}
          >
            Previous
          </button>

          {currentQuestionIndex < totalQuestions - 1 ? (
            <button
              onClick={() => setCurrentQuestionIndex((prev) => prev + 1)}
              className="px-6 py-3 rounded-lg bg-indigo-600 hover:bg-indigo-800 text-white font-semibold text-lg transition-all"
            >
              Next
            </button>
          ) : (
            <button
              onClick={confirmSubmit} // ✅ Show Confirmation Modal
              className="px-6 py-3 rounded-lg bg-green-600 hover:bg-green-800 text-white font-semibold text-lg transition-all"
            >
              Submit Quiz
            </button>
          )}
        </div>
      </div>

      {/* Right: Question Navigation Panel */}
      <div className="w-1/4 ml-6 bg-white p-6 rounded-lg shadow-lg flex flex-col space-y-3">
        <h2 className="text-lg font-semibold text-gray-800 text-center mb-4">
          Questions
        </h2>
        <div className="grid grid-cols-5 gap-2">
          {quiz.questions.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentQuestionIndex(index)}
              className={`px-4 py-2 rounded-lg text-sm font-bold ${
                currentQuestionIndex === index
                  ? "bg-blue-500 text-white"
                  : answers[index]
                  ? "bg-green-500 text-white"
                  : "bg-gray-300 hover:bg-gray-400"
              }`}
            >
              {index + 1}
            </button>
          ))}
        </div>
      </div>

      {/* ✅ Submit Confirmation Modal */}
      <SubmitConfirmationModal
        isOpen={showSubmitModal}
        onClose={() => setShowSubmitModal(false)}
        onConfirm={handleSubmit}
        hasUnanswered={checkUnansweredQuestions()}
        isSubmitting={isSubmitting}
      />
    </div>
  );
};

export default TopicBasedQuizPage;
