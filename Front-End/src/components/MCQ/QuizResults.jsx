import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import api from "../axios/api"; // Import API handler
import QuizLoadingScreen from "./loadingPage/QuizLoadingScreen"; // Import loading screen component

const difficultyColors = {
  easy: "bg-green-200 text-green-800",
  medium: "bg-yellow-200 text-yellow-800",
  hard: "bg-red-200 text-red-800",
};

const QuizResults = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const userId = location.state?.userId;
  const quizId = location.state?.quizId;
  const attemptNumber = location.state?.attemptNumber; // Passed from history page
  const token = localStorage.getItem("token");
  console.log("Results:", userId, quizId, attemptNumber);

  // Initialize results state (null at start)
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true); //  Start with loading as true

  useEffect(() => {
    if (userId && quizId && attemptNumber) {
      fetchAttemptResults(); // Fetch from backend if responseId exists
    } else {
      setResults(null);
      setLoading(false);
    }
  }, [userId && quizId && attemptNumber]);

  // Function to fetch attempt results from the backend
  const fetchAttemptResults = async () => {
    try {
      setLoading(true); //  Show loading when fetching data
      const response = await api.get(
        `/responses/quiz_attempt_results/${userId}/${quizId}/${attemptNumber}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.data) {
        setResults(response.data);
        console.log(response.data);
        localStorage.setItem("quizResults", JSON.stringify(response.data)); //  Overwrite localStorage with fresh data
      } else {
        setResults(null);
      }
      setLoading(false); //  Stop loading after data is fetched
    } catch (error) {
      console.error("Error fetching quiz attempt:", error);
      setResults(null);
      setLoading(false); //  Stop loading on error
    }
  };

  if (loading) {
    return (
      <div className="mt-0 sm:mt-20">
        <QuizLoadingScreen />
      </div>
    );
  }

  if (!results || !results.summary) {
    return (
      <div className="text-center p-10">
        <p className="text-red-600 font-semibold text-xl">
          ⚠️ Quiz results not found.
        </p>
        <button
          onClick={() => navigate("/mcq-home")}
          className="mt-6 bg-blue-500 hover:bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold transition"
        >
          Back to Home
        </button>
      </div>
    );
  }
  // Compute difficulty counts from responses
  const difficultyCounts = results.responses.reduce(
    (acc, { difficulty }) => {
      acc[difficulty] = (acc[difficulty] || 0) + 1;
      return acc;
    },
    { easy: 0, medium: 0, hard: 0 }
  );

  return (
    <div className="min-h-screen flex flex-col items-center mt-0 sm:mt-20 bg-gradient-to-br from-gray-100 to-gray-300 p-6">
      <motion.div
        className="max-w-3xl w-full bg-white p-8 rounded-2xl shadow-xl border border-gray-300"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h2 className="text-4xl font-extrabold text-center text-green-600">
          Quiz Results
        </h2>

        {/* Summary Section */}
        <div className="mt-6 bg-gray-100 p-4 rounded-lg shadow-sm">
          <p className="text-lg font-semibold text-gray-700 text-center">
            Attempt Number:{" "}
            <span className="text-indigo-600">{results.attempt_number}</span>
          </p>
          <p className="text-lg font-semibold text-gray-700 text-center mt-2">
            Correct Answers:{" "}
            <span className="text-green-600">
              {results.summary.correct_answers}
            </span>{" "}
            / {results.summary.total_questions}
          </p>
          <p className="text-lg font-semibold text-gray-700 text-center">
            Accuracy:{" "}
            <span className="text-indigo-600">{results.summary.accuracy}%</span>
          </p>
          <p className="text-lg font-semibold text-gray-700 text-center">
            Total Time:{" "}
            <span className="text-indigo-600">
              {results.summary.total_time} sec
            </span>
          </p>
          <div className="flex justify-between mb-4 p-2 bg-gray-100 rounded-lg">
            <span className="text-green-600 font-semibold">
              Easy: {difficultyCounts.easy}
            </span>
            <span className="text-yellow-600 font-semibold">
              Medium: {difficultyCounts.medium}
            </span>
            <span className="text-red-600 font-semibold">
              Hard: {difficultyCounts.hard}
            </span>
          </div>
        </div>

        {/* Questions & Answers Section */}
        <div className="mt-8 space-y-6">
          {results.responses.map((response, index) => {
            const isCorrect = response.is_correct;
            return (
              <motion.div
                key={index}
                className="relative bg-white p-5 rounded-xl shadow-lg border border-gray-200"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
              >
                {/* Difficulty Tag - Now it will be positioned correctly */}
                <span
                  className={`absolute top-2 right-2 text-xs px-3 py-1 rounded-full font-semibold ${
                    difficultyColors[response.difficulty]
                  }`}
                >
                  {response.difficulty.charAt(0).toUpperCase() +
                    response.difficulty.slice(1)}
                </span>

                <h3 className="text-xl font-bold text-gray-800 mt-6">
                  {index + 1}. {response.question_text}
                </h3>

                <div className="mt-3 space-y-2">
                  {Object.entries(response.options).map(([letter, option]) => {
                    if (!option) return null; // Ignore empty options

                    const isSelected = response.selected_answer === letter;
                    const isCorrectAnswer = response.correct_answer === letter;

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
                <div className="mt-3 text-lg font-semibold">
                  {isCorrect ? (
                    <p className="text-green-600">✅ Correct Answer!</p>
                  ) : (
                    <p className="text-red-600">
                      ❌ Incorrect! The correct answer is{" "}
                      <span className="font-bold text-green-500">
                        {response.correct_answer}.{" "}
                        {response.options[response.correct_answer]}
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
