import React, { useEffect, useState } from "react";
import api from "../../axios/api";
import { motion } from "framer-motion";
import { FaBookOpen, FaCheckCircle, FaArrowRight } from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import QuizLoadingScreen from "../loadingPage/QuizLoadingScreen";

const TopicBasedQuizzes = () => {
  const [quizzes, setQuizzes] = useState([]);
  const [completedQuizzes, setCompletedQuizzes] = useState([]); // Ensure this is always an array
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const userId = JSON.parse(localStorage.getItem("user"))?.user_id;
  const token = localStorage.getItem("token");

  useEffect(() => {
    fetchQuizzes();
  }, []);

  const fetchQuizzes = async () => {
    try {
      const response = await api.get("/topic/topic_quiz/all", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setQuizzes(response.data || []);

      const attemptsResponse = await api.get(
        `/topic/quiz/completed/${userId}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      setCompletedQuizzes(attemptsResponse.data?.completed_quizzes || []);
    } catch (error) {
      console.error("Error fetching topic quizzes:", error);
      setCompletedQuizzes([]);
    } finally {
      setLoading(false);
    }
  };

  const handleQuizAction = (quiz) => {
    if (completedQuizzes.includes(quiz.quiz_id)) {
      navigate("/topic_quiz/results", {
        state: { quizId: quiz.quiz_id, topicName: quiz.topic_name },
      });
    } else {
      console.log("Starting quiz:", quiz.quiz_id);
      navigate("/topic_quiz", {
        state: { quizId: quiz.quiz_id, topicName: quiz.topic_name },
      });
    }
  };

  if (loading) {
    return (
      <div className="mt-0 sm:mt-20">
        <QuizLoadingScreen />
      </div>
    );
  }

  return (
    <div className="min-h-screen mt-0 sm:mt-20 p-10 bg-gradient-to-br from-indigo-50 to-indigo-100 text-gray-900">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center mb-10"
      >
        <h1 className="text-4xl font-extrabold text-indigo-700">
          📚 Topic-Based Quizzes
        </h1>
        <p className="text-gray-600 mt-2 text-lg">
          Test your knowledge with topic-based quizzes! Each quiz can be
          **attempted once**, and you can view your results afterward.
        </p>
      </motion.div>

      <div className="max-w-3xl mx-auto space-y-6">
        {quizzes.map((quiz) => (
          <motion.div
            key={quiz.quiz_id}
            className="bg-white p-6 rounded-xl shadow-md flex items-center justify-between border border-gray-200 hover:shadow-lg transition-all"
            whileHover={{ scale: 1.02 }}
          >
            <div className="flex items-center gap-3">
              <FaBookOpen className="text-indigo-600 text-3xl" />
              <h2 className="text-xl font-semibold text-gray-700">
                {quiz.topic_name}
              </h2>
            </div>
            <motion.button
              onClick={() => handleQuizAction(quiz)}
              className={`px-5 py-2 flex items-center gap-2 rounded-lg text-white transition-all ${
                completedQuizzes.includes(quiz.quiz_id)
                  ? "bg-gray-600 hover:bg-gray-700"
                  : "bg-indigo-600 hover:bg-indigo-800"
              }`}
            >
              {completedQuizzes.includes(quiz.quiz_id) ? (
                <>
                  View Results <FaCheckCircle className="text-green-300" />
                </>
              ) : (
                <>
                  Start Quiz <FaArrowRight />
                </>
              )}
            </motion.button>
          </motion.div>
        ))}
      </div>

      <div className="text-center mt-10">
        <p className="text-gray-600">
          ✅ Once you complete a quiz, you can view your results at any time.
        </p>
      </div>
    </div>
  );
};

export default TopicBasedQuizzes;
