import React, { useEffect, useState } from "react";
import api from "../../axios/api";
import { motion } from "framer-motion";
import {
  FaBookOpen,
  FaArrowRight,
  FaEye,
  FaMedal,
  FaChevronDown,
  FaChevronUp,
} from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import QuizLoadingScreen from "../loadingPage/QuizLoadingScreen";

const UNIT_NAME_MAP = {
  "Unit 01": "Unit 01 - Introduction to Biology",
  "Unit 02": "Unit 02 - Chemical and cellular basis of life",
  "Unit 03": "Unit 03 - Evolution and diversity of organisms",
  "Unit 04": "Unit 04 - Plant form and function",
  "Unit 05": "Unit 05 - Animal form and function",
  "Unit 06": "Unit 06 - Genetics",
  "Unit 07": "Unit 07 - Molecular Biology and Recombinant DNA Technology",
  "Unit 08": "Unit 08 - Environmental Biology",
  "Unit 09": "Unit 09 - Microbiology",
  "Unit 10": "Unit 10 - Applied Biology",
};

const UnitBasedQuizzes = () => {
  const [statusMap, setStatusMap] = useState({});
  const [expandedUnits, setExpandedUnits] = useState({});
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const userId = JSON.parse(localStorage.getItem("user"))?.user_id;
  const token = localStorage.getItem("token");

  useEffect(() => {
    fetchQuizStatus();
  }, []);

  const fetchQuizStatus = async () => {
    try {
      const res = await api.get(`/topic/unit_quiz/status/${userId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setStatusMap(res.data || {});
    } catch (err) {
      console.error("Error fetching unit quiz status:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleStartQuiz = async (unitKey) => {
    try {
      const res = await api.get(`/topic/unit_quiz/generate/${userId}`, {
        headers: { Authorization: `Bearer ${token}` },
        params: { unit: unitKey, question_count: 10 },
      });

      const { quiz_id, questions } = res.data;

      navigate("/unit_quiz", {
        state: {
          quizId: quiz_id,
          unitName: unitKey,
          questions,
        },
      });
    } catch (err) {
      console.error("Failed to generate quiz:", err);
      alert("Failed to generate quiz. Please try again.");
    }
  };

  const handleViewResult = (quizId, unitName) => {
    navigate("/unit_quiz/results", { state: { quizId, unitName } });
  };

  const toggleUnit = (unitKey) => {
    setExpandedUnits((prev) => ({ ...prev, [unitKey]: !prev[unitKey] }));
  };

  if (loading) {
    return <QuizLoadingScreen />;
  }

  return (
    <div className="min-h-screen mt-0 sm:mt-24 p-6 bg-gradient-to-br from-green-50 to-green-100 text-gray-900">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center mb-10"
      >
        <h1 className="text-3xl sm:text-5xl font-extrabold text-green-700">
          🌱 Unit-Based Quizzes
        </h1>
        <p className="text-gray-600 mt-2 text-lg">
          Attempt quizzes from each unit. Take multiple quizzes and track your
          performance.
        </p>
      </motion.div>

      <div className="w-full max-w-7xl mx-auto space-y-10 px-4 sm:px-8">
        {Object.entries(UNIT_NAME_MAP).map(([unitKey, unitName]) => {
          const quizzes = statusMap[unitKey] || [];
          const bestScore = quizzes.reduce(
            (max, q) => Math.max(max, q.score),
            0
          );
          const isExpanded = expandedUnits[unitKey];
          return (
            <motion.div
              key={unitKey}
              className="bg-white p-8 rounded-2xl shadow-md border border-gray-200 hover:shadow-lg transition-all"
              whileHover={{ scale: 1.02 }}
            >
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-center gap-4">
                  <FaBookOpen className="text-green-600 text-4xl" />
                  <div>
                    <h2 className="text-3xl text-gray-800">{unitName}</h2>
                    {quizzes.length > 0 && (
                      <p className="text-lg text-gray-600 mt-1 font-medium">
                        🏅 Best Score: {bestScore}/10
                      </p>
                    )}
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row gap-3 mt-4 sm:mt-0">
                  {quizzes.length > 0 && (
                    <motion.button
                      onClick={() => toggleUnit(unitKey)}
                      className="inline-flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#140342] text-[#140342]
                            font-semibold rounded-lg 
                            hover:bg-[#140342] hover:text-white hover:rounded-2xl hover:shadow-lg transition-all duration-300 group"
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      {isExpanded ? (
                        <>
                          <FaChevronUp className="transition-transform duration-300 transform" />
                          Hide History
                        </>
                      ) : (
                        <>
                          <FaChevronDown className="transition-transform duration-300 transform" />
                          Show History
                        </>
                      )}
                    </motion.button>
                  )}
                  <button
                    onClick={() => handleStartQuiz(unitKey)}
                    className="flex items-center justify-center gap-2 px-6 py-3 border-2 border-green-600 bg-green-600 text-white font-semibold rounded-lg 
             transition-transform duration-300 hover:scale-105 hover:bg-green-700"
                  >
                    Start New Quiz <FaArrowRight />
                  </button>
                </div>
              </div>

              {isExpanded && quizzes.length > 0 && (
                <div className="mt-6 text-gray-800">
                  <p className="text-xl font-semibold mb-4">📘 Quiz History</p>
                  <ul className="space-y-4">
                    {[...quizzes]
                      .sort(
                        (a, b) =>
                          new Date(b.submitted_at) - new Date(a.submitted_at)
                      )
                      .map((quiz, index) => (
                        <li
                          key={index}
                          className="flex flex-col sm:flex-row sm:justify-between sm:items-center bg-gray-50 p-5 rounded-xl border border-gray-300"
                        >
                          <div className="flex flex-col sm:flex-row sm:items-center gap-4">
                            <span className="font-semibold text-lg">
                              Quiz {quizzes.length - index}
                            </span>
                            <span className="text-gray-600 text-base">
                              {new Date(quiz.submitted_at).toLocaleString()}
                            </span>
                            <span className="text-green-700 font-semibold text-lg">
                              Score: {quiz.score}/{quiz.total_questions}
                            </span>
                            {quiz.score === bestScore && bestScore > 0 && (
                              <FaMedal
                                className="text-yellow-500 text-xl"
                                title="Top Score"
                              />
                            )}
                          </div>
                          <motion.button
                            onClick={() =>
                              handleViewResult(quiz.quiz_id, unitName)
                            }
                            className="inline-flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#140342] text-[#140342]
                            font-semibold rounded-lg 
                            hover:bg-[#140342] hover:text-white hover:rounded-2xl hover:shadow-lg transition-all duration-300 group"
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                          >
                            View Result
                          </motion.button>
                        </li>
                      ))}
                  </ul>
                </div>
              )}
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};

export default UnitBasedQuizzes;
