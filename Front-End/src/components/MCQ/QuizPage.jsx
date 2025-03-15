import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import api from "../axios/api";
import SubmitConfirmationModal from "./models/SubmitConfirmationModal";

const QuizPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { quizId } = location.state || {};
  const [questions, setQuestions] = useState(location.state?.questions || null);
  const [showSubmitModal, setShowSubmitModal] = useState(false); // ✅ State for modal
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeSpent, setTimeSpent] = useState({});
  const [startTime, setStartTime] = useState(Date.now());
  const [unanswered, setUnanswered] = useState([]);
  const [timer, setTimer] = useState(2700); // 45 minutes timer

  const user = JSON.parse(localStorage.getItem("user"));
  const token = localStorage.getItem("token");

  useEffect(() => {
    if (!quizId) {
      console.warn("Quiz ID is missing. Redirecting...");
      navigate("/mcq-home");
    } else if (!questions) {
      fetchQuizData();
    }
  }, [quizId, questions, navigate]);

  const fetchQuizData = async () => {
    try {
      const response = await api.get(`/responses/get_quiz/${quizId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.data) {
        setQuestions(response.data.questions);
      } else {
        console.error("Quiz not found.");
        navigate("/mcq-home");
      }
    } catch (error) {
      console.error("Error fetching quiz:", error);
      navigate("/mcq-home");
    }
  };

  if (!questions || questions.length === 0) {
    return (
      <div className="text-center text-white">
        <p>⚠️ No quiz data available. Redirecting...</p>
      </div>
    );
  }

  const currentQuestion = questions[currentQuestionIndex];
  const optionsMap = ["A", "B", "C", "D", "E"];

  const filteredOptions = [
    currentQuestion.option1,
    currentQuestion.option2,
    currentQuestion.option3,
    currentQuestion.option4,
    currentQuestion.option5,
  ].filter((option) => option !== "N/A");

  // ✅ Update time spent on a question
  const updateTimeSpent = (index) => {
    const endTime = Date.now();
    const timeTaken = (endTime - startTime) / 1000;

    setTimeSpent((prev) => ({
      ...prev,
      [index]: (prev[index] || 0) + timeTaken,
    }));

    setStartTime(Date.now());
  };

  // ✅ Handle Answer Selection
  const handleAnswerSelect = (letter) => {
    setAnswers({ ...answers, [currentQuestionIndex]: letter });
  };

  // ✅ Handle Next & Previous Button Clicks
  const handleNext = () => {
    updateTimeSpent(currentQuestionIndex);
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex((prev) => prev + 1);
    }
  };

  const handlePrevious = () => {
    updateTimeSpent(currentQuestionIndex);
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex((prev) => prev - 1);
    }
  };

  // ✅ Handle quiz submission
  const handleSubmit = async () => {
    updateTimeSpent(currentQuestionIndex);

    // Check for unanswered questions
    const unansweredIndexes = questions
      .map((_, index) => (!answers.hasOwnProperty(index) ? index + 1 : null))
      .filter((index) => index !== null);

    setUnanswered(unansweredIndexes);

    if (unansweredIndexes.length > 0) {
      if (
        !window.confirm(
          `⚠️ You have unanswered questions: ${unansweredIndexes.join(
            ", "
          )}. Submit anyway?`
        )
      ) {
        return;
      }
    }

    const quizResults = questions.map((q, index) => ({
      question_text: q.question_text,
      selected_answer: answers[index] || "No Answer",
      time_taken: timeSpent[index] || 0,
    }));

    console.log("📤 Sending Quiz Data:", {
      user_id: user.user_id,
      quiz_id: quizId,
      responses: quizResults,
    });
    try {
      const headers = {
        Authorization: `Bearer ${token}`,
      };
      const response = await api.post(
        "http://127.0.0.1:8000/responses/submit_quiz/",
        {
          user_id: user.user_id,
          quiz_id: quizId,
          responses: quizResults,
        },
        { headers }
      );

      console.log("Quiz Results from Backend:", response.data);

      navigate("/quiz-results", {
        state: {
          userId: response.data.user_id,
          quizId: response.data.quiz_id,
          attemptNumber: response.data.attempt_number,
        },
      });
    } catch (error) {
      console.error("Error submitting quiz:", error);
    }
  };

  useEffect(() => {
    if (timer <= 0) {
      handleSubmit(); // Auto-submit when time runs out
    }

    const interval = setInterval(() => {
      setTimer((prev) => prev - 1);
    }, 1000);

    return () => clearInterval(interval); // ✅ Cleanup to avoid memory leaks
  }, [timer]);

  return (
    <div className="min-h-screen flex flex-col justify-center items-center sm:mt-0 lg:mt-20 bg-gradient-to-br from-gray-100 to-gray-50 text-gray-900 p-5">
      <motion.div
        className="max-w-2xl w-full bg-white p-8 rounded-2xl shadow-xl border border-gray-300"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* ✅ Timer */}
        <div className="text-center text-xl font-bold text-red-600">
          ⏳ Time Left: {Math.floor(timer / 60)}:
          {String(timer % 60).padStart(2, "0")}
        </div>
        {/* ✅ Question Progress */}
        <div className="w-full bg-gray-300 h-2 rounded-full my-4">
          <motion.div
            className="bg-purple-500 h-2 rounded-full"
            style={{
              width: `${
                ((currentQuestionIndex + 1) / questions.length) * 100
              }%`,
            }}
            initial={{ width: 0 }}
            animate={{
              width: `${
                ((currentQuestionIndex + 1) / questions.length) * 100
              }%`,
            }}
            transition={{ duration: 0.5 }}
          />
        </div>

        <h2 className="text-3xl font-extrabold mb-4 text-center tracking-wider text-indigo-700">
          Question {currentQuestionIndex + 1} of {questions.length}
        </h2>
        <p className="text-lg font-semibold text-center mb-6 text-gray-700">
          {currentQuestion.question_text}
        </p>

        {/* ✅ Answer Choices */}
        <div className="mt-4 space-y-3">
          {filteredOptions.map((option, index) => {
            const letter = optionsMap[index];
            return (
              <motion.button
                key={index}
                onClick={() => handleAnswerSelect(letter)}
                whileTap={{ scale: 0.95 }}
                className={`w-full px-5 py-3 rounded-lg border transition-all duration-300 text-lg font-semibold 
                  ${
                    answers[currentQuestionIndex] === letter
                      ? "bg-purple-500 border-purple-700 text-white shadow-lg"
                      : "bg-indigo-100 hover:bg-indigo-200 border-indigo-300 text-indigo-800"
                  }`}
              >
                {letter}. {option}
              </motion.button>
            );
          })}
        </div>

        {/* ✅ Navigation Buttons */}
        <div className="flex justify-between mt-8">
          <button
            onClick={handlePrevious}
            className={`px-6 py-3 rounded-lg font-semibold text-lg transition duration-300 
              ${
                currentQuestionIndex === 0
                  ? "bg-gray-400 opacity-50 cursor-not-allowed"
                  : "bg-indigo-200 hover:bg-indigo-300 text-indigo-800"
              }`}
            disabled={currentQuestionIndex === 0}
          >
            Previous
          </button>

          {currentQuestionIndex < questions.length - 1 ? (
            <button
              onClick={handleNext}
              className="px-6 py-3 rounded-lg bg-purple-500 hover:bg-purple-600 font-semibold text-lg shadow-lg text-white transition duration-300"
            >
              Next
            </button>
          ) : (
            <button
              onClick={() => setShowSubmitModal(true)}
              className="px-6 py-3 rounded-lg bg-green-500 hover:bg-green-600 font-semibold text-lg shadow-lg text-white transition duration-300"
            >
              Submit Quiz
            </button>
          )}
        </div>
      </motion.div>
      <SubmitConfirmationModal
        isOpen={showSubmitModal}
        onClose={() => setShowSubmitModal(false)}
        onConfirm={handleSubmit} // ✅ Call handleSubmit when confirmed
      />
    </div>
  );
};

export default QuizPage;
