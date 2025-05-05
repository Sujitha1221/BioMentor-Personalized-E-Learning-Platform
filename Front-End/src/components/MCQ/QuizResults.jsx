import React, { useEffect, useState, useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";
import api from "../axios/api"; // Import API handler
import QuizLoadingScreen from "./loadingPage/QuizLoadingScreen"; // Import loading screen component
import { FaCheckCircle, FaTimesCircle } from "react-icons/fa";

const difficultyColors = {
  easy: "bg-green-200 text-green-800",
  medium: "bg-yellow-200 text-yellow-800",
  hard: "bg-red-200 text-red-800",
};

const QuizResults = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const printRef = useRef();
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
      fetchAttemptResults(); // Fetch from backend if userId, quizId, and attemptNumber are available
    } else {
      setResults(null);
      setLoading(false);
    }
  }, [userId, quizId, attemptNumber]); // ✅ Proper dependency array

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

  const formatTime = (seconds) => {
    if (seconds < 60) {
      return `${seconds.toFixed(1)} sec`; // Show seconds for values < 60
    }
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes} min ${remainingSeconds} sec`; // Show MM:SS for values >= 60
  };

  // PDF generator:
  const handleGeneratePDF = () => {
    if (!results?.responses) return;

    const pdf = new jsPDF({
      unit: "mm",
      format: "a4",
      orientation: "portrait",
    });
    const pw = pdf.internal.pageSize.getWidth();
    const ph = pdf.internal.pageSize.getHeight();
    const margin = 10;
    const maxW = pw - margin * 2;
    const lh = 7; // line height in mm
    let y = margin;

    // — Header —
    pdf.setFontSize(16);
    pdf.text(`Quiz Results — Attempt ${results.attempt_number}`, margin, y);
    y += lh * 1.5;
    pdf.setFontSize(12);
    pdf.text(
      `Score: ${results.summary.correct_answers} / ${results.summary.total_questions} (${results.summary.accuracy}%)`,
      margin,
      y
    );
    y += lh * 2;

    results.responses.forEach((resp, idx) => {
      // 1) Question lines
      pdf.setFont(undefined, "bold");
      const qLines = pdf.splitTextToSize(
        `Question ${idx + 1} : ${resp.question_text}`,
        maxW
      );
      const qH = qLines.length * lh;

      // 2) Options lines
      pdf.setFont(undefined, "normal");
      let optsLineCount = 0;
      ["A", "B", "C", "D", "E"].forEach((L) => {
        const t = resp.options[L] || "";
        optsLineCount += t ? pdf.splitTextToSize(t, maxW - 8).length : 0;
      });
      // +1 for "Answer options:" label
      const optsH = optsLineCount * lh + lh;

      // 3) Correct answer as one block
      const caFull = `Correct answer: ${resp.correct_answer}. ${
        resp.options[resp.correct_answer] || ""
      }`;
      const caLines = pdf.splitTextToSize(caFull, maxW);
      const caH = caLines.length * lh;

      // total height of this question‐block
      const blockH =
        qH +
        lh + // question bottom padding
        optsH +
        lh + // options + bottom padding
        caH +
        lh * 1.5; // correct answer + extra bottom padding

      // — page break if needed —
      if (y + blockH > ph - margin) {
        pdf.addPage();
        y = margin;
      }

      // — draw question —
      pdf.setFont(undefined, "bold");
      pdf.text(qLines, margin, y);
      y += qH + lh;

      // — draw options header —
      pdf.text("Answer options:", margin, y);
      y += lh;

      // — draw each option —
      pdf.setFont(undefined, "normal");
      ["A", "B", "C", "D", "E"].forEach((L) => {
        const t = resp.options[L];
        if (!t) return;
        const wrapped = pdf.splitTextToSize(t, maxW - 8);
        pdf.text(`${L}:`, margin + 2, y);
        pdf.text(wrapped, margin + 10, y);
        y += wrapped.length * lh;
      });

      // spacer before correct answer
      y += lh;

      // — draw correct answer in one wrapped block —
      pdf.setFont(undefined, "bold");
      pdf.text(caLines, margin, y);
      y += caH + lh * 1.5;
    });

    pdf.save(`quiz-results-attempt-${results.attempt_number}.pdf`);
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
          ⚠️ Unable to load quiz results. Please try again later.
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
        ref={printRef}
        className="max-w-5xl w-full bg-white p-8 rounded-2xl shadow-xl border border-gray-300"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h2 className="text-4xl font-extrabold text-center text-green-600">
          🌿Quiz Results
        </h2>

        {/* Summary Section */}
        <div className="mt-6 bg-gray-100 p-4 rounded-lg shadow-sm">
          <p className="text-lg font-semibold text-gray-700 text-center">
            Attempt Number:{" "}
            <span className="text-indigo-600">{results.attempt_number}</span>
          </p>
          <p className="text-lg font-semibold text-gray-700 text-center mt-2">
            ✅ Correct Answers:{" "}
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
            ⏱️ Total Time:{" "}
            <span className="text-indigo-600">
              {formatTime(results.summary.total_time)} sec
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

        {/* PDF Button */}
        <div className="text-center mt-4">
          <button
            onClick={handleGeneratePDF}
            title="Download your quiz results as a PDF file"
            aria-label="Download quiz results as PDF"
            className="mt-3 sm:mt-0 px-4 py-2 bg-[#140342] text-white rounded-lg hover:bg-[#140342] transition-all"
          >
            📄 Download Quiz Results (PDF)
          </button>
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
                <span
                  className={`absolute top-2 left-2 text-s px-3 py-1 rounded-full`}
                >
                  Time Spent on this question: {formatTime(response.time_taken)}
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
                    <p className="text-green-600 flex items-center">
                      <FaCheckCircle className="mr-2" /> Correct Answer!
                    </p>
                  ) : (
                    <div className="mt-3 text-lg font-semibold flex items-start gap-2 text-red-600">
                      <FaTimesCircle className="mt-1 text-xl" />
                      <span>
                        Incorrect! The correct answer is:{" "}
                        <span className="text-green-700 font-bold">
                          {response.correct_answer}.{" "}
                          {response.options[response.correct_answer]}
                        </span>
                      </span>
                    </div>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Back Button */}
        <button
          onClick={() => navigate("/mcq-home")}
          className="mt-8 w-full bg-green-700 hover:bg-green-900 text-white py-3 rounded-lg font-semibold transition"
        >
          Back to Home
        </button>
      </motion.div>
    </div>
  );
};

export default QuizResults;
