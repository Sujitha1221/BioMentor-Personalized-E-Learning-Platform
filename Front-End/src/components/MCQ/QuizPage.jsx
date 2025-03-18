import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import api from "../axios/api";
import SubmitConfirmationModal from "./models/SubmitConfirmationModal";

const difficultyColors = {
  easy: "bg-green-200 text-green-800",
  medium: "bg-yellow-200 text-yellow-800",
  hard: "bg-red-200 text-red-800",
};

const QuizPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { quizId } = location.state || {};
  const [questions, setQuestions] = useState(location.state?.questions || null);
  const [showSubmitModal, setShowSubmitModal] = useState(false); //  State for modal
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

  //  Update time spent on a question
  const updateTimeSpent = (index) => {
    return new Promise((resolve) => {
      const endTime = Date.now();
      const timeTaken = (endTime - startTime) / 1000;

      setTimeSpent((prev) => {
        const updatedTime = {
          ...prev,
          [index]: (prev[index] || 0) + timeTaken,
        };
        console.log(
          `⏳ Time Updated for Question ${index + 1}:`,
          updatedTime[index]
        ); // Debugging log
        resolve(updatedTime); // Ensure we resolve with the new state
        return updatedTime;
      });

      setStartTime(Date.now());
    });
  };

  //  Handle Answer Selection
  const handleAnswerSelect = (letter) => {
    setAnswers({ ...answers, [currentQuestionIndex]: letter });
  };

  //  Handle Next & Previous Button Clicks
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

  const handleQuestionSelect = (index) => {
    updateTimeSpent(currentQuestionIndex); // Update time before switching
    setCurrentQuestionIndex(index);
  };

  //  Handle quiz submission
  const handleSubmit = async () => {
    console.log("Ensuring last question time is recorded before submitting...");
    await updateTimeSpent(currentQuestionIndex);

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
        "responses/submit_quiz/",
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

    return () => clearInterval(interval); //  Cleanup to avoid memory leaks
  }, [timer]);

  return (
    <div className="min-h-screen flex flex-col sm:flex-row justify-center items-start sm:items-center sm:mt-0 lg:mt-20 bg-gradient-to-br from-gray-100 to-gray-50 text-gray-900 p-5">
      <motion.div
        className="w-full sm:w-3/4 bg-white p-8 rounded-2xl shadow-xl border border-gray-300"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/*  Timer */}
        <div className="text-center text-xl font-bold text-red-600">
          ⏳ Time Left: {Math.floor(timer / 60)}:
          {String(timer % 60).padStart(2, "0")}
        </div>
        {/*  Question Progress */}
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
        <div className="relative">
          <span
            className={`absolute top-2 right-2 text-xs px-3 py-1 rounded-full font-semibold ${
              difficultyColors[currentQuestion?.difficulty] ||
              "bg-gray-200 text-gray-800"
            }`}
          >
            {currentQuestion?.difficulty || "Unknown"}
          </span>
        </div>

        <h2 className="text-3xl font-extrabold mb-4 text-center tracking-wider text-indigo-700">
          Question {currentQuestionIndex + 1} of {questions.length}
        </h2>
        <p className="text-lg font-semibold text-center mb-6 text-gray-700">
          {currentQuestion.question_text}
        </p>

        {/*  Answer Choices */}
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

        {/*  Navigation Buttons */}
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
      <div className="w-full sm:w-1/4 bg-white p-6 rounded-lg shadow-lg sm:ml-6 sm:mt-[-400px]">
        <h2 className="text-lg font-semibold text-gray-800 text-center mb-4">
          Questions
        </h2>
        <div className="grid grid-cols-5 sm:grid-cols-4 gap-2">
          {questions.map((_, index) => (
            <button
              key={index}
              onClick={() => handleQuestionSelect(index)}
              className={`px-3 py-2 rounded-lg text-xs sm:text-sm font-bold ${
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

      <SubmitConfirmationModal
        isOpen={showSubmitModal}
        onClose={() => setShowSubmitModal(false)}
        onConfirm={handleSubmit} //  Call handleSubmit when confirmed
      />
    </div>
  );
};

export default QuizPage;
