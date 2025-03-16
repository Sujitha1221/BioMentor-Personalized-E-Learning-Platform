import React, { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import QuizIntroductionModal from "./models/QuizIntroductionModal";
import {
  FaChartBar,
  FaQuestionCircle,
  FaHistory,
  FaBookOpen,
} from "react-icons/fa";
import adaptiveMcq from "../../assets/mcq-images/adaptive_mcq.jpg";
import performanceDashboard from "../../assets/mcq-images/performance_dashboard.jpg";
import quizHistory from "../../assets/mcq-images/quiz_history.jpg";
import TopicBased from "../../assets/mcq-images/topic-based.jpg";
import { useNavigate } from "react-router-dom";
import Hero from "./Hero/Hero";
const MCQHomePage = () => {
  const [isQuizIntroductionModalOpen, setIsQuizIntroductionModalOpen] =
    useState(false);
  const [isFirstQuiz, setIsFirstQuiz] = useState(true);
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user"));
  const token = localStorage.getItem("token");
  const firstSectionRef = useRef(null);
  useEffect(() => {
    if (!user || !token) {
      navigate("/");
    }
  }, [user, token, navigate]);
  useEffect(() => {
    const quizCount = localStorage.getItem("quizCount") || 0;
    setIsFirstQuiz(quizCount === 0);
  }, []);

  return (
    <>
      <Hero firstSectionRef={firstSectionRef} />
      <div
        ref={firstSectionRef}
        className="p-12 bg-gradient-to-br from-gray-100 to-gray-50 min-h-screen flex flex-col items-center gap-20 md:mt-5"
      >
        {/* Start Quiz Section */}
        <div className="mt-6 max-w-7xl w-full grid grid-cols-1 md:grid-cols-2 gap-20 items-center text-center md:text-left">
          <motion.div
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="flex flex-col items-center md:items-start order-1 md:order-1"
          >
            <div className="p-6 bg-indigo-100 rounded-full shadow-lg flex items-center justify-center w-20 h-20 mb-4 animate-pulse">
              <FaQuestionCircle className="text-5xl text-purple-600" />
            </div>
            <h1 className="text-4xl font-extrabold text-gray-800 leading-tight tracking-wide">
              Master Your Knowledge with Adaptive Quizzes
            </h1>
            <p className="text-gray-600 text-lg mt-4 leading-relaxed">
              Take personalized quizzes that adjust based on your answers. Track
              your improvements, identify your strengths, and enhance your
              learning journey.
            </p>
            <div className="mt-4 flex gap-3 flex-wrap justify-center md:justify-start">
              {[
                "ADAPTIVE LEARNING",
                "REAL-TIME FEEDBACK",
                "ACCURATE SCORING",
                "IMPROVEMENT ANALYSIS",
              ].map((tag) => (
                <span
                  key={tag}
                  className="text-sm px-4 py-2 bg-indigo-200 rounded-full text-purple-800 font-semibold shadow-md"
                >
                  {tag}
                </span>
              ))}
            </div>
            <motion.button
              onClick={() => setIsQuizIntroductionModalOpen(true)}
              className="mt-6 px-10 py-4 bg-purple-700 text-white text-lg font-bold rounded-2xl shadow-lg hover:bg-purple-900 transition-all duration-300 hover:scale-105"
            >
              Start Your Quiz
            </motion.button>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="order-2 md:order-2"
          >
            <img
              src={adaptiveMcq}
              alt="Quiz Illustration"
              className="rounded-xl shadow-lg"
            />
          </motion.div>
        </div>
        <QuizIntroductionModal
          isOpen={isQuizIntroductionModalOpen}
          onClose={() => setIsQuizIntroductionModalOpen(false)}
          isFirstQuiz={isFirstQuiz}
        />

        {/* Quiz History Section */}
        <div className="max-w-7xl w-full grid grid-cols-1 md:grid-cols-2 gap-20 items-center text-center md:text-left">
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="order-2 md:order-1"
          >
            <img
              src={quizHistory}
              alt="History Illustration"
              className="rounded-xl shadow-lg"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="flex flex-col items-center md:items-start order-1 md:order-1"
          >
            <div className="p-6 bg-purple-100 rounded-full shadow-lg flex items-center justify-center w-20 h-20 mb-4 animate-pulse">
              <FaHistory className="text-5xl text-indigo-600" />
            </div>
            <h1 className="text-4xl font-extrabold text-gray-800 leading-tight tracking-wide">
              Explore Your Quiz History
            </h1>
            <p className="text-gray-600 text-lg mt-4 leading-relaxed">
              Keep track of all quizzes you have attempted. Reattempt previous
              quizzes, compare your scores, and measure your improvement over
              time.
            </p>
            <div className="mt-4 flex gap-3 flex-wrap justify-center md:justify-start">
              {[
                "REVIEW ATTEMPTS",
                "TRACK PROGRESS",
                "COMPARE SCORES",
                "IMPROVEMENT ANALYSIS",
              ].map((tag) => (
                <span
                  key={tag}
                  className="text-sm px-4 py-2 bg-purple-200 rounded-full text-indigo-800 font-semibold shadow-md"
                >
                  {tag}
                </span>
              ))}
            </div>
            <motion.button
              onClick={() => (window.location.href = "/quiz-history")}
              className="mt-6 px-10 py-4 bg-indigo-700 text-white text-lg font-bold rounded-2xl shadow-lg hover:bg-indigo-900 transition-all duration-300 hover:scale-105"
            >
              View Quiz History
            </motion.button>
          </motion.div>
        </div>

        {/* Performance Dashboard Section */}
        <div className="max-w-7xl w-full grid grid-cols-1 md:grid-cols-2 gap-20 items-center text-center md:text-left">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="flex flex-col items-center md:items-start order-1 md:order-1"
          >
            <div className="p-6 bg-green-100 rounded-full shadow-lg flex items-center justify-center w-20 h-20 mb-4 animate-pulse">
              <FaChartBar className="text-5xl text-green-600" />
            </div>
            <h1 className="text-4xl font-extrabold text-gray-800 leading-tight tracking-wide">
              View Your Performance Dashboard
            </h1>
            <p className="text-gray-600 text-lg mt-4 leading-relaxed">
              Track your progress, see detailed analytics, and get insights into
              your learning trends.
            </p>
            <div className="mt-4 flex gap-3 flex-wrap justify-center md:justify-start">
              {[
                "DETAILED ANALYTICS",
                "WEAK AREAS",
                "STRENGTH TRACKING",
                "PERFORMANCE TRENDS",
              ].map((tag) => (
                <span
                  key={tag}
                  className="text-sm px-4 py-2 bg-green-200 rounded-full text-green-800 font-semibold shadow-md"
                >
                  {tag}
                </span>
              ))}
            </div>
            <motion.button
              onClick={() => (window.location.href = "/performance-dashboard")}
              className="mt-6 px-10 py-4 bg-green-700 text-white text-lg font-bold rounded-2xl shadow-lg hover:bg-green-900 transition-all duration-300 hover:scale-105"
            >
              Open Dashboard
            </motion.button>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="order-2 md:order-2"
          >
            <img
              src={performanceDashboard}
              alt="Quiz Illustration"
              className="rounded-xl shadow-lg"
            />
          </motion.div>
        </div>
        {/*  New Section: Practice Topic-wise MCQ Questions */}
        <div className="max-w-7xl w-full grid grid-cols-1 md:grid-cols-2 gap-20 items-center text-center md:text-left">
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="order-2 md:order-1"
          >
            <img
              src={TopicBased}
              alt="Topic-wise MCQ Illustration"
              className="rounded-xl shadow-lg"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="flex flex-col items-center md:items-start order-1 md:order-2"
          >
            <div className="p-6 bg-yellow-100 rounded-full shadow-lg flex items-center justify-center w-20 h-20 mb-4 animate-pulse">
              <FaBookOpen className="text-5xl text-yellow-600" />
            </div>
            <h1 className="text-4xl font-extrabold text-gray-800 leading-tight tracking-wide">
              Practice Topic-wise MCQ Questions
            </h1>
            <p className="text-gray-600 text-lg mt-4 leading-relaxed">
              Strengthen your knowledge by practicing MCQs from different
              topics. Choose a subject, test your skills, and improve your
              understanding.
            </p>
            <div className="mt-4 flex gap-3 flex-wrap justify-center md:justify-start">
              {[
                "SUBJECT-BASED PRACTICE",
                "TOPIC-WISE TESTS",
                "IMPROVE ACCURACY",
                "FOCUSED LEARNING",
              ].map((tag) => (
                <span
                  key={tag}
                  className="text-sm px-4 py-2 bg-yellow-200 rounded-full text-yellow-800 font-semibold shadow-md"
                >
                  {tag}
                </span>
              ))}
            </div>
            <motion.button
              onClick={() => navigate("/topic-quizzes")}
              className="mt-6 px-10 py-4 bg-yellow-700 text-white text-lg font-bold rounded-2xl shadow-lg hover:bg-yellow-900 transition-all duration-300 hover:scale-105"
            >
              Practice MCQs
            </motion.button>
          </motion.div>
        </div>
      </div>
    </>
  );
};

export default MCQHomePage;
