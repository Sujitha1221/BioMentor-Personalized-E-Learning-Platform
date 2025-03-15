import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import api from "../../axios/api.js";
import { FaCheckCircle, FaTimesCircle } from "react-icons/fa";
import QuizLoadingScreen from "../loadingPage/QuizLoadingScreen";

const QuizResults = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const userId = JSON.parse(localStorage.getItem("user"))?.user_id;
  const quizId = location.state?.quizId;
  const token = localStorage.getItem("token");

  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!userId || !quizId) {
      navigate("/");
      return;
    }
    fetchQuizResults();
  }, [userId, quizId]);

  const fetchQuizResults = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/topic/quiz_topic/results/${quizId}`, {
        params: { user_id: userId },
        headers: { Authorization: `Bearer ${token}` },
      });
      setResults(response.data);
    } catch (error) {
      console.error("Error fetching quiz results:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="mt-0 sm:mt-20">
        <QuizLoadingScreen />
      </div>
    );
  }

  if (!results) {
    return (
      <div className="text-center mt-0 sm:mt-20 py-20">
        <p className="text-red-600 text-lg font-semibold">
          ⚠️ No quiz results found.
        </p>
        <button
          onClick={() => navigate("/")}
          className="mt-4 px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition"
        >
          Back to Home
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen mt-0 sm:mt-20 p-10 bg-gradient-to-br from-gray-100 to-gray-300 text-gray-900">
      <motion.div
        className="max-w-4xl mx-auto bg-white p-8 rounded-2xl shadow-xl border border-gray-300"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h2 className="text-4xl font-extrabold text-center text-indigo-700">
          📜 Quiz Results
        </h2>

        <div className="mt-6 bg-gray-100 p-4 rounded-lg shadow">
          <p className="text-lg font-semibold text-gray-700 text-center">
            📅 Submission Date:
            <span className="text-indigo-600">
              {" "}
              {new Date(results.submitted_at).toLocaleString()}
            </span>
          </p>
          <p className="text-lg font-semibold text-gray-700 text-center">
            🎯 Score: <span className="text-green-600">{results.score}</span> /{" "}
            {results.responses.length}
          </p>
        </div>

        {/* Questions & Answers Section */}
        <div className="mt-8 space-y-6">
          {results.responses.map((response, index) => {
            const {
              question_text,
              options,
              selected_answer,
              correct_answer,
              is_correct,
            } = response;

            return (
              <motion.div
                key={index}
                className="bg-white p-5 rounded-xl shadow-lg border border-gray-200"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
              >
                <h3 className="text-xl font-bold text-gray-800">
                  {index + 1}. {question_text}
                </h3>

                <div className="mt-3 space-y-2">
                  {Object.entries(options).map(([letter, option]) => {
                    const isSelected = selected_answer === letter;
                    const isCorrectAnswer = correct_answer === letter;

                    return (
                      <p
                        key={letter}
                        className={`px-4 py-2 rounded-lg text-lg font-medium transition-all
                          ${
                            isCorrectAnswer
                              ? "bg-green-500 text-white shadow-md"
                              : isSelected
                              ? "bg-red-500 text-white shadow-md"
                              : "bg-gray-200 text-gray-800"
                          }
                        `}
                      >
                        {letter}. {option}
                      </p>
                    );
                  })}
                </div>

                {/* Show feedback */}
                <div className="mt-3 text-lg font-semibold flex items-center">
                  {is_correct ? (
                    <p className="text-green-600 flex items-center">
                      <FaCheckCircle className="mr-2" /> Correct Answer!
                    </p>
                  ) : (
                    <p className="text-red-600 flex items-center">
                      <FaTimesCircle className="mr-2" /> Incorrect! The correct
                      answer is:
                      <span className="font-bold text-green-500 ml-2">
                        {correct_answer}. {options[correct_answer]}
                      </span>
                    </p>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Back Button */}
        <button
          onClick={() => navigate("/mcq-home")}
          className="mt-8 w-full bg-indigo-700 hover:bg-indigo-900 text-white py-3 rounded-lg font-semibold transition"
        >
          Back to Home
        </button>
      </motion.div>
    </div>
  );
};

export default QuizResults;
