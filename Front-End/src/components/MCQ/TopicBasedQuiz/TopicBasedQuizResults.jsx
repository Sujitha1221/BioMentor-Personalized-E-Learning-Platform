import React, { useEffect, useState, useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import api from "../../axios/api.js";
import jsPDF from "jspdf";
import ExplainModal from "../models/ExplanationModel.jsx";
import { FaCheckCircle, FaTimesCircle } from "react-icons/fa";
import QuizLoadingScreen from "../loadingPage/QuizLoadingScreen";

const UnitQuizResults = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const printRef = useRef();
  const token = localStorage.getItem("token");
  const quizId = location.state?.quizId;
  const [isExplainOpen, setIsExplainOpen] = useState(false);
  const [explanationText, setExplanationText] = useState("");
  const [isLoadingExplanation, setIsLoadingExplanation] = useState(false);
  const [verifiedAnswer, setVerifiedAnswer] = useState(null);

  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!quizId || !token) {
      navigate("/");
      return;
    }
    fetchQuizResults();
  }, [quizId]);

  const fetchQuizResults = async () => {
    try {
      setLoading(true);
      const res = await api.get(`/topic/unit_quiz/results/${quizId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setResults(res.data);
    } catch (err) {
      console.error("Error fetching unit quiz results:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePDF = () => {
    if (!results) return;

    const pdf = new jsPDF({
      unit: "mm",
      format: "a4",
      orientation: "portrait",
    });
    const pw = pdf.internal.pageSize.getWidth();
    const ph = pdf.internal.pageSize.getHeight();
    const margin = 10;
    const maxW = pw - margin * 2;
    const lh = 7; // line-height in mm
    let y = margin;

    // Header
    pdf.setFontSize(16);
    pdf.text(`${results.unit_name} - Results`, margin, y);
    y += lh * 1.5;

    pdf.setFontSize(12);
    pdf.text(
      `Submitted at: ${new Date(results.submitted_at).toLocaleString()}`,
      margin,
      y
    );
    y += lh;
    pdf.text(
      `Score: ${results.correct_count} / ${results.total_questions}`,
      margin,
      y
    );
    y += lh * 2;

    // Loop through questions
    results.responses.forEach((resp, idx) => {
      // 1) Question lines
      pdf.setFont(undefined, "bold");
      const qLines = pdf.splitTextToSize(
        `${idx + 1}. ${resp.question_text}`,
        maxW
      );
      const qH = qLines.length * lh;

      // 2) Count option lines
      pdf.setFont(undefined, "normal");
      let optsLines = 0;
      ["A", "B", "C", "D", "E"].forEach((L) => {
        const t = resp.options[L] || "";
        if (t) optsLines += pdf.splitTextToSize(t, maxW - 10).length;
      });
      const optsH = optsLines * lh + lh; // + header line

      // 3) Correct answer block
      const caText = `Correct answer: ${resp.correct_answer}. ${
        resp.options[resp.correct_answer] || ""
      }`;
      const caLines = pdf.splitTextToSize(caText, maxW);
      const caH = caLines.length * lh;

      // Total block height (with padding)
      const blockH =
        qH +
        lh * 0.5 + // space after question
        optsH +
        lh * 0.5 + // space before correct answer
        caH +
        lh * 1; // space after question block

      // Page break if needed
      if (y + blockH > ph - margin) {
        pdf.addPage();
        y = margin;
      }

      // Draw question
      pdf.setFont(undefined, "bold");
      pdf.text(qLines, margin, y);
      y += qH + lh * 0.5;

      // Draw options header
      pdf.text("Answer options:", margin, y);
      y += lh;

      // Draw each option
      pdf.setFont(undefined, "normal");
      ["A", "B", "C", "D", "E"].forEach((L) => {
        const t = resp.options[L];
        if (!t) return;
        const wrapped = pdf.splitTextToSize(t, maxW - 10);
        pdf.text(`${L}:`, margin + 2, y);
        pdf.text(wrapped, margin + 10, y);
        y += wrapped.length * lh;
      });

      y += lh * 0.5;

      // Draw correct answer
      pdf.setFont(undefined, "bold");
      pdf.text(caLines, margin, y);
      y += caH + lh * 1;
    });

    pdf.save(`${results.unit_name.replace(/\s+/g, "_")}_results.pdf`);
  };

  const handleDownloadCSV = () => {
    if (!results?.responses) return;

    const headers = [
      "Question",
      "Option A",
      "Option B",
      "Option C",
      "Option D",
      "Option E",
      "Correct Answer",
    ];

    const rows = results.responses.map((resp) => {
      const question = `"${resp.question_text.replace(/"/g, '""')}"`;

      const getOption = (letter) => resp.options[letter] || "";

      const correct = `${resp.correct_answer}. ${getOption(
        resp.correct_answer
      )}`;

      return [
        question,
        getOption("A"),
        getOption("B"),
        getOption("C"),
        getOption("D"),
        getOption("E"),
        correct,
      ];
    });

    const csvContent = [
      headers.join(","),
      ...rows.map((r) =>
        r.map((cell) => `"${cell.replace(/"/g, '""')}"`).join(",")
      ),
    ].join("\n");

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute(
      "download",
      `quiz_results_attempt_${results.attempt_number}.csv`
    );
    link.click();
  };

  // Function to fetch explanation for a question
  const fetchExplanation = async (questionText, options, claimedAnswer) => {
    setIsLoadingExplanation(true);
    setIsExplainOpen(true);

    try {
      const response = await api.post(
        `/explanations/mcq/verify_and_explain`,
        {
          question: questionText,
          options,
          claimed_answer: claimedAnswer,
        },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      const { explanation, predicted_answer } = response.data;

      setExplanationText(explanation || "No explanation found.");
      setVerifiedAnswer(predicted_answer || null);
    } catch (err) {
      console.error("Failed to fetch explanation:", err);
      setExplanationText("Error fetching explanation.");
      setVerifiedAnswer(null);
    } finally {
      setIsLoadingExplanation(false);
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
          ⚠️ Unable to load quiz results. Please try again later.
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
    <div className="min-h-screen mt-0 sm:mt-20 p-10 bg-gradient-to-br from-green-50 to-green-200 text-gray-900">
      <motion.div
        ref={printRef}
        className="max-w-5xl mx-auto bg-white p-8 rounded-2xl shadow-xl border border-gray-300"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h2 className="text-4xl font-extrabold text-center text-green-700">
          🌿 {results.unit_name} - Results
        </h2>

        <div className="mt-6 bg-gray-100 p-4 rounded-lg shadow">
          <p className="text-lg font-semibold text-gray-700 text-center">
            📅 Submitted At:
            <span className="text-green-600">
              {" "}
              {new Date(results.submitted_at).toLocaleString()}
            </span>
          </p>
          <p className="text-lg font-semibold text-gray-700 text-center">
            ✅ Correct:{" "}
            <span className="text-green-600">{results.correct_count}</span> /{" "}
            {results.total_questions}
          </p>
        </div>
        {/* PDF Button */}
        <div className="text-center mt-4 space-x-4">
          <button
            onClick={handleGeneratePDF}
            title="Download as PDF"
            className="px-4 py-2 bg-[#140342] text-white rounded-lg hover:bg-[#1f1b46] transition-all"
          >
            📄 Download PDF
          </button>
          <button
            onClick={handleDownloadCSV}
            title="Download as CSV"
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-all"
          >
            🧾 Download CSV
          </button>
        </div>

        {/* Questions & Feedback */}
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
                    const isCorrect = correct_answer === letter;

                    return (
                      <p
                        key={letter}
                        className={`px-4 py-2 rounded-lg text-lg font-medium transition-all ${
                          isCorrect
                            ? "bg-green-500 text-white shadow-md"
                            : isSelected
                            ? "bg-red-500 text-white shadow-md"
                            : "bg-gray-200 text-gray-800"
                        }`}
                      >
                        {letter}. {option}
                      </p>
                    );
                  })}
                </div>

                <div className="mt-3 text-lg font-semibold flex items-center">
                  {is_correct ? (
                    <p className="text-green-600 flex items-center">
                      <FaCheckCircle className="mr-2" /> Correct Answer!
                    </p>
                  ) : (
                    <div className="mt-3 text-lg font-semibold flex items-start gap-2 text-red-600">
                      <FaTimesCircle className="mt-1 text-xl" />
                      <span>
                        Incorrect! The correct answer is:{" "}
                        <span className="text-green-700 font-bold">
                          {correct_answer}. {options[correct_answer]}
                        </span>
                      </span>
                    </div>
                  )}
                </div>
                <button
                  onClick={() =>
                    fetchExplanation(
                      response.question_text,
                      response.options,
                      response.correct_answer
                    )
                  }
                  className="mt-4 px-4 py-2 bg-[#140342] text-white rounded-lg hover:bg-[#140342] transition"
                >
                  {is_correct
                    ? "😊 What makes this the right answer?"
                    : "🤔 Where did I go wrong?"}
                </button>
              </motion.div>
            );
          })}
        </div>

        <button
          onClick={() => navigate("/mcq-home")}
          className="mt-8 w-full bg-green-700 hover:bg-green-900 text-white py-3 rounded-lg font-semibold transition"
        >
          Back to Home
        </button>
      </motion.div>
      <ExplainModal
        isOpen={isExplainOpen}
        onClose={() => setIsExplainOpen(false)}
        explanation={explanationText}
        loading={isLoadingExplanation}
        verifiedAnswer={verifiedAnswer}
      />
    </div>
  );
};

export default UnitQuizResults;
