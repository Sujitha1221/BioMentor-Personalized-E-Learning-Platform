import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { FaTimes } from "react-icons/fa";
import api from "../../axios/api.js";
import { useNavigate } from "react-router-dom";
import LoadingScreen from "../loadingPage/LoadingScreen.jsx";

const QuizIntroductionModal = ({ isOpen, onClose }) => {
  const navigate = useNavigate();
  const [hasPreviousQuizzes, setHasPreviousQuizzes] = useState(false);
  const [loading, setLoading] = useState(true);
  const [isGeneratingQuiz, setIsGeneratingQuiz] = useState(false);
  const [quizReady, setQuizReady] = useState(false);

  const user = JSON.parse(localStorage.getItem("user"));
  const token = localStorage.getItem("token");
  const userId = user?.user_id;

  useEffect(() => {
    const fetchQuizHistory = async () => {
      if (!userId) return;
      try {
        const headers = {
          Authorization: `Bearer ${token}`,
        };
        const response = await api.get(
          `responses/users/${userId}/has_previous_quiz`,
          {
            headers,
          }
        );
        console.log("📚 Quiz history:", response.data);
        setHasPreviousQuizzes(response.data.has_previous_quiz);
      } catch (error) {
        console.error("⚠️ Error fetching quiz history:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchQuizHistory();
  }, [userId, token]);

  const handleStartQuiz = async () => {
    try {
      setIsGeneratingQuiz(true);
      let response;
      const headers = {
        Authorization: `Bearer ${token}`,
      };
      if (hasPreviousQuizzes) {
        response = await api.get(`/quiz/generate_adaptive_mcqs/${userId}/20`, {
          headers,
        });
      } else {
        response = await api.get(`/mcqs/generate_mcqs/${userId}`, { headers });
      }
      // Wait for actual response instead of fixed timeout
      setQuizReady(true);
      navigate("/quiz-page", {
        state: { quizId: response.data.quiz_id, questions: response.data.mcqs },
      });
    } catch (error) {
      console.error("❌ Error starting quiz:", error);
    }
  };

  if (!isOpen) return null;
  if (isGeneratingQuiz) return <LoadingScreen quizReady={quizReady} />;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <motion.div
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="bg-white rounded-lg shadow-xl p-6 w-11/12 md:w-1/2"
      >
        <div className="flex justify-between items-center border-b pb-4">
          <h2 className="text-2xl font-bold text-gray-800">
            {loading
              ? "🔍 Checking your quiz history..."
              : hasPreviousQuizzes
              ? "🎯 Welcome back! Ready for another challenge?"
              : "🎉 Welcome to your first quiz! Let's get started!"}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-600 hover:text-red-600"
          >
            <FaTimes size={20} />
          </button>
        </div>
        <div className="mt-4 text-gray-700 text-lg">
          {loading ? (
            <p>
              ⏳ We are checking your previous quiz attempts. Please wait...
            </p>
          ) : hasPreviousQuizzes ? (
            <p>
              👋 Great to see you again! This quiz will adapt to your previous
              performance to help you improve. Focus and do your best! 💪 Ensure
              you answer all the questions to complete the quiz successfully.
            </p>
          ) : (
            <p>
              📝 Since this is your first quiz, take your time and answer
              carefully. Avoid using external resources—the goal is to
              understand your knowledge level so we can tailor future quizzes
              for you. 🚀
            </p>
          )}
        </div>
        <div className="mt-6 flex justify-end gap-4">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-gray-300 text-gray-800 font-semibold rounded-lg shadow-md hover:bg-gray-400"
          >
            ❌ Cancel
          </button>
          <button
            onClick={handleStartQuiz}
            className="px-6 py-2 bg-purple-700 text-white font-semibold rounded-lg shadow-md hover:bg-purple-900 transition-all"
            disabled={loading}
          >
            {loading ? "⏳ Loading..." : "🚀 Start Quiz"}
          </button>
        </div>
      </motion.div>
    </div>
  );
};

export default QuizIntroductionModal;
