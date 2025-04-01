import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import SubmitConfirmationModal from "../models/ConfirmationModal.jsx";

const UnitQuizPage = () => {
  const { quizId, unitName, questions } = useLocation().state || {};
  const navigate = useNavigate();
  const userId = JSON.parse(localStorage.getItem("user"))?.user_id;
  const token = localStorage.getItem("token");

  const [answers, setAnswers] = useState({});
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleAnswerSelect = (answer) => {
    setAnswers((prev) => ({ ...prev, [currentQuestionIndex]: answer }));
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      const responses = questions.map((q, index) => ({
        question_text: q.question_text,
        selected_answer: answers[index] || "Not Answered",
      }));

      await fetch(`/api/topic/unit_quiz/submit`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          user_id: userId,
          quiz_id: quizId,
          responses,
        }),
      });

      navigate("/unit_quiz/results", { state: { quizId, unitName } });
    } catch (err) {
      console.error("Error submitting quiz:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const confirmSubmit = () => setShowSubmitModal(true);
  const checkUnanswered = () =>
    questions.filter((_, i) => !answers[i]).length > 0;

  const currentQuestion = questions[currentQuestionIndex];

  return (
    <div className="min-h-screen mt-0 sm:mt-24 flex flex-col sm:flex-row p-4 sm:p-6 bg-gradient-to-br from-green-100 to-green-200 text-gray-900">
      <div className="w-full sm:w-3/4 bg-white p-6 rounded-lg shadow-lg">
        <motion.h1
          className="text-2xl sm:text-3xl font-bold text-green-700 mb-6"
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          📘 {unitName} Quiz
        </motion.h1>

        <div>
          <h3 className="text-lg font-semibold mb-4">
            {currentQuestionIndex + 1}. {currentQuestion.question_text}
          </h3>
          <div className="space-y-2">
            {Object.entries(currentQuestion.options).map(([key, option]) => (
              <button
                key={key}
                onClick={() => handleAnswerSelect(key)}
                className={`block w-full px-4 py-2 text-left rounded-lg border ${
                  answers[currentQuestionIndex] === key
                    ? "bg-green-600 text-white"
                    : "bg-gray-200 hover:bg-gray-300"
                }`}
              >
                {key}. {option}
              </button>
            ))}
          </div>
        </div>

        <div className="flex justify-between mt-6">
          <button
            disabled={currentQuestionIndex === 0}
            onClick={() =>
              setCurrentQuestionIndex((prev) => Math.max(prev - 1, 0))
            }
            className={`px-4 py-2 rounded-lg font-semibold ${
              currentQuestionIndex === 0
                ? "bg-gray-300"
                : "bg-green-600 text-white hover:bg-green-800"
            }`}
          >
            Previous
          </button>
          {currentQuestionIndex < questions.length - 1 ? (
            <button
              onClick={() => setCurrentQuestionIndex((prev) => prev + 1)}
              className="px-4 py-2 rounded-lg bg-green-600 text-white hover:bg-green-800 font-semibold"
            >
              Next
            </button>
          ) : (
            <button
              onClick={confirmSubmit}
              className="px-4 py-2 rounded-lg bg-[#140342] text-white hover:bg-[#140342] font-semibold"
            >
              Submit Quiz
            </button>
          )}
        </div>
      </div>

      <div className="w-full sm:w-1/4 mt-6 sm:mt-0 sm:ml-6 bg-white p-4 rounded-lg shadow-lg">
        <h2 className="text-xl font-semibold mb-4 text-center">Questions</h2>
        <div className="grid grid-cols-5 sm:grid-cols-4 gap-2">
          {questions.map((_, i) => (
            <button
              key={i}
              onClick={() => setCurrentQuestionIndex(i)}
              className={`px-3 py-2 rounded-lg text-sm font-bold ${
                currentQuestionIndex === i
                  ? "bg-green-500 text-white"
                  : answers[i]
                  ? "bg-[#140342] text-white"
                  : "bg-gray-300 hover:bg-gray-400"
              }`}
            >
              {i + 1}
            </button>
          ))}
        </div>
      </div>

      <SubmitConfirmationModal
        isOpen={showSubmitModal}
        onClose={() => setShowSubmitModal(false)}
        onConfirm={handleSubmit}
        hasUnanswered={checkUnanswered()}
        isSubmitting={isSubmitting}
      />
    </div>
  );
};

export default UnitQuizPage;
