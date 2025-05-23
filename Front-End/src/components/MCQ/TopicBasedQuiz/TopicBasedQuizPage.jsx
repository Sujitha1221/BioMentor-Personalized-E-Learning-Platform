import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import SubmitConfirmationModal from "../models/ConfirmationModal.jsx";
import api from "../../axios/api.js";

const UnitQuizPage = () => {
  const { quizId, unitName, questions } = useLocation().state || {};
  const navigate = useNavigate();
  const userId = JSON.parse(localStorage.getItem("user"))?.user_id;
  const token = localStorage.getItem("token");

  const [answers, setAnswers] = useState({});
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [speaking, setSpeaking] = useState(false);

  const speakText = (text) => {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.onstart = () => setSpeaking(true);
      utterance.onend = () => setSpeaking(false);
      utterance.onerror = () => setSpeaking(false);

      window.speechSynthesis.speak(utterance);
    } else {
      alert("Sorry, your browser doesn't support text-to-speech.");
    }
  };

  const handleSpeak = () => {
    const questionText = currentQuestion.question_text;
    const optionsText = Object.entries(currentQuestion.options)
      .map(([key, value]) => `Option ${key}: ${value}`)
      .join(". ");
    const textToRead = `Question ${
      currentQuestionIndex + 1
    }. ${questionText}. ${optionsText}`;
    speakText(textToRead);
  };

  const stopSpeaking = () => {
    if (window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel();
      setSpeaking(false);
    }
  };

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
  
      const response = await api.post(
        `/topic/quiz/submit/${userId}`,
        {
          // user_id: userId,
          quiz_id: quizId,
          responses,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
  
      console.log("✅ Quiz submitted:", response.data);
  
      // Navigate to results page
      navigate("/unit_quiz/results", {
        state: {
          quizId,
          unitName,
        },
      });
    } catch (err) {
      console.error("❌ Error submitting quiz:", err);
      alert("Failed to submit quiz. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };
  

  const confirmSubmit = () => setShowSubmitModal(true);
  const checkUnanswered = () =>
    questions.filter((_, i) => !answers[i]).length > 0;

  const currentQuestion = questions[currentQuestionIndex];

  return (
    <div className="min-h-screen mt-0 sm:mt-20 flex flex-col sm:flex-row p-4 sm:p-6 bg-gradient-to-br from-green-100 to-green-200 text-gray-900">
      <motion.div
        className="w-full sm:w-3/4 bg-white p-8 rounded-2xl shadow-xl border border-gray-300"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <motion.h1
          className="text-2xl sm:text-3xl font-bold text-green-700 mb-6"
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          📘 {unitName} Quiz
        </motion.h1>

        <div className="relative w-full">
          <h3 className="text-3xl font-extrabold mb-4 text-center tracking-wider text-[#140342]">
            Question {currentQuestionIndex + 1} of {questions.length}
          </h3>
        </div>

        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between mb-4">
          <p className="text-lg font-semibold text-center text-gray-700 w-full sm:text-center sm:flex-1">
            {currentQuestion.question_text}
          </p>
          <div className="mt-3 sm:mt-0 sm:ml-4 flex justify-center sm:justify-end w-full sm:w-auto whitespace-nowrap">
            {speaking ? (
              <button
                onClick={stopSpeaking}
                className="flex items-center gap-2 bg-red-200 hover:bg-red-300 text-red-800 px-4 py-2 rounded-md font-semibold"
              >
                🛑 Stop
              </button>
            ) : (
              <button
                onClick={handleSpeak}
                className="flex items-center gap-2 bg-[#140342] text-white px-4 py-2 rounded-md font-semibold"
              >
                🔊 Speak
              </button>
            )}
          </div>
        </div>

        <div className="mt-4 space-y-3">
          {Object.entries(currentQuestion.options).map(([key, option]) => (
            <motion.button
              key={key}
              onClick={() => handleAnswerSelect(key)}
              whileTap={{ scale: 0.95 }}
              className={`w-full px-5 py-3 rounded-lg border transition-all duration-300 text-lg font-semibold 
                ${
                  answers[currentQuestionIndex] === key
                    ? "bg-[#140342] border-blue-900 text-white shadow-lg"
                    : "bg-indigo-100 hover:bg-indigo-200 border-indigo-300 text-[#140342]"
                }`}
            >
              {key}. {option}
            </motion.button>
          ))}
        </div>

        <div className="flex flex-col sm:flex-row justify-between gap-3 mt-8">
          <button
            disabled={currentQuestionIndex === 0}
            onClick={() =>
              setCurrentQuestionIndex((prev) => Math.max(prev - 1, 0))
            }
            className={`w-full sm:w-auto px-6 py-3 rounded-lg font-semibold text-lg flex gap-2 items-center justify-center ${
              currentQuestionIndex === 0
                ? "bg-gray-400 opacity-50 cursor-not-allowed"
                : "bg-indigo-200 hover:bg-indigo-300 text-blue-900"
            }`}
          >
            Previous
          </button>

          {currentQuestionIndex < questions.length - 1 ? (
            <button
              onClick={() => setCurrentQuestionIndex((prev) => prev + 1)}
              className="w-full sm:w-auto px-6 py-3 rounded-lg bg-[#140342] hover:bg-[#140342] font-semibold text-lg shadow-lg text-white flex items-center justify-center gap-2"
            >
              Next
            </button>
          ) : (
            <button
              onClick={confirmSubmit}
              className="w-full sm:w-auto px-6 py-3 rounded-lg bg-green-500 hover:bg-green-600 font-semibold text-lg shadow-lg text-white flex items-center justify-center gap-2"
            >
              Submit Quiz
            </button>
          )}
        </div>
      </motion.div>

      <div className="w-full sm:w-1/4 mt-6 sm:mt-0 sm:ml-6 bg-white p-6 rounded-lg shadow-lg">
        <h2 className="text-lg font-semibold text-gray-800 text-center mb-4">
          Questions
        </h2>
        <div className="grid grid-cols-5 sm:grid-cols-4 gap-2">
          {questions.map((_, i) => (
            <button
              key={i}
              onClick={() => setCurrentQuestionIndex(i)}
              className={`px-3 py-2 rounded-lg text-xs sm:text-sm font-bold ${
                currentQuestionIndex === i
                  ? "bg-[#140342] text-white"
                  : answers[i]
                  ? "bg-green-500 text-white"
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
