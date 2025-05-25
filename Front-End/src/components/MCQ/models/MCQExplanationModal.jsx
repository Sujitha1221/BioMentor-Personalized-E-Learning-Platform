import React, { useState, useEffect } from "react";
import { FaCheckCircle, FaCopy, FaTimes } from "react-icons/fa";
import { Sparkles, ShieldCheck, ArrowLeft } from "lucide-react";
import api from "../../axios/api";
import AlertMessage from "../../Alert/Alert";
import ModalLoadingScreen from "../../LoadingScreen/ModalLoadingScreen";

const MCQExplanationModal = ({ mode, onBack, onClose }) => {
  const [usePasteMode, setUsePasteMode] = useState(true);
  const [question, setQuestion] = useState("");
  const [options, setOptions] = useState({ A: "", B: "", C: "", D: "", E: "" });
  const [claimedAnswer, setClaimedAnswer] = useState("");
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [alert, setAlert] = useState({ message: "", type: "" });
  const [pasteBlock, setPasteBlock] = useState("");

  const validateInputs = () => {
    if (!question.trim() || Object.values(options).some((opt) => !opt.trim())) {
      setAlert({
        message: "Please complete the question and all 5 options.",
        type: "warning",
      });
      return false;
    }
    if (mode === "verify") {
      const valid = ["A", "B", "C", "D", "E"];
      if (!valid.includes(claimedAnswer.toUpperCase())) {
        setAlert({
          message: "Claimed answer must be one of A, B, C, D, or E.",
          type: "warning",
        });
        return false;
      }
    }
    return true;
  };

  const handleExplainOnly = async () => {
    if (!validateInputs()) return;
    setLoading(true);
    try {
      const res = await api.post(`/explanations/mcq/explain_only`, {
        question,
        options,
      });
      setResponse(res.data);
    } catch (error) {
      setAlert({
        message: error.response?.data?.detail || "Something went wrong.",
        type: "error",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyAndExplain = async () => {
    if (!validateInputs()) return;
    setLoading(true);
    try {
      const res = await api.post(`/explanations/mcq/verify_and_explain`, {
        question,
        options,
        claimed_answer: claimedAnswer.toUpperCase(),
      });
      setResponse(res.data);
    } catch (error) {
      setAlert({
        message: error.response?.data?.detail || "Something went wrong.",
        type: "error",
      });
    } finally {
      setLoading(false);
    }
  };

  const handlePasteMCQBlock = (text) => {
    if (!text) return;
    const lines = text
      .trim()
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean);

    let q = "";
    const opts = { A: "", B: "", C: "", D: "", E: "" };

    lines.forEach((line) => {
      // Match A) or A. or A: format
      const alphaMatch = line.match(/^([A-Ea-e])[\)\.\:\-]?\s+(.*)/);
      if (alphaMatch) {
        const letter = alphaMatch[1].toUpperCase();
        opts[letter] = alphaMatch[2].trim();
        return;
      }

      // Match 1) or 1. or 1: format
      const numberMatch = line.match(/^([1-5])[\)\.\:\-]?\s+(.*)/);
      if (numberMatch) {
        const numberToLetter = { 1: "A", 2: "B", 3: "C", 4: "D", 5: "E" };
        const letter = numberToLetter[numberMatch[1]];
        opts[letter] = numberMatch[2].trim();
        return;
      }

      // If it's not an option line, and we don't yet have the question
      if (!q) {
        q = line;
      }
    });

    setQuestion(q);
    setOptions((prev) => ({ ...prev, ...opts }));

    if (Object.values(opts).filter(Boolean).length < 5) {
      setAlert({
        message: "Some options may be missing. Please double-check.",
        type: "warning",
      });
    }
  };

  const copyToClipboard = () => {
    if (response?.explanation) {
      navigator.clipboard.writeText(response.explanation);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-30 flex justify-center items-center p-4 z-50">
      <div className="bg-white rounded-2xl shadow-xl w-[750px] p-8 max-w-[95%] sm:p-6 space-y-6 overflow-y-auto max-h-[90vh] relative">
        {/* ❌ Close Button */}
        <button
          className="absolute top-4 right-4 text-gray-500 hover:text-gray-700 text-xl"
          onClick={onClose}
        >
          <FaTimes />
        </button>

        {/* ✅ Alert */}
        {alert.message && (
          <AlertMessage
            message={alert.message}
            type={alert.type}
            onClose={() => setAlert({ message: "", type: "" })}
          />
        )}

        {/* ✅ Title */}
        <h2 className="text-2xl font-bold text-gray-800">
          {mode === "verify"
            ? "Verify & Explain MCQ"
            : "Generate MCQ Explanation"}
        </h2>

        {/* ✅ Mode Toggle */}
        <div className="flex items-center gap-4 mt-2 mb-4">
          <label className="font-medium text-gray-700">Input Mode:</label>
          <div className="flex gap-3">
            <button
              onClick={() => setUsePasteMode(true)}
              className={`px-4 py-1 rounded-full text-sm font-semibold border ${
                usePasteMode
                  ? "bg-[#140342] text-white"
                  : "bg-white text-gray-700"
              }`}
            >
              Paste Full MCQ
            </button>
            <button
              onClick={() => setUsePasteMode(false)}
              className={`px-4 py-1 rounded-full text-sm font-semibold border ${
                !usePasteMode
                  ? "bg-[#140342] text-white"
                  : "bg-white text-gray-700"
              }`}
            >
              Manual Input
            </button>
          </div>
        </div>

        {/* ✅ Paste Mode */}
        {usePasteMode ? (
          <div className="relative mb-4">
            <textarea
              rows={6}
              className="w-full border border-gray-300 p-2 rounded-lg pr-12"
              placeholder={`Paste full MCQ like:\nWhat is the ...?\nA) Option\nB) Option\nC) Option\nD) Option\nE) Option`}
              value={pasteBlock}
              onChange={(e) => setPasteBlock(e.target.value)}
              onBlur={() => handlePasteMCQBlock(pasteBlock)}
            />
            {pasteBlock && (
              <button
                onClick={() => setPasteBlock("")}
                className="absolute top-2 right-2 text-sm text-gray-500 hover:text-red-600"
                title="Clear prompt"
              >
                <FaTimes />
              </button>
            )}
          </div>
        ) : (
          <>
            <label className="font-medium">Question:</label>
            <input
              className="w-full border border-gray-300 p-2 rounded-lg mb-2"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
            />
            {["A", "B", "C", "D", "E"].map((key) => (
              <input
                key={key}
                placeholder={`Option ${key}`}
                value={options[key]}
                className="w-full border border-gray-300 p-2 rounded-lg mb-2"
                onChange={(e) =>
                  setOptions({ ...options, [key]: e.target.value })
                }
              />
            ))}
          </>
        )}

        {mode === "verify" && (
          <input
            className="w-full border border-gray-300 p-2 rounded-lg mb-2"
            placeholder="Claimed Answer (A–E)"
            value={claimedAnswer}
            onChange={(e) => setClaimedAnswer(e.target.value.toUpperCase())}
          />
        )}

        {/* ✅ Buttons */}
        <div className="flex gap-4">
          <button
            onClick={onBack}
            className="flex-1 px-4 py-2 bg-gray-600 text-white rounded-lg flex items-center justify-center gap-2"
          >
            <ArrowLeft size={16} /> Back
          </button>

          <button
            onClick={
              mode === "verify" ? handleVerifyAndExplain : handleExplainOnly
            }
            disabled={loading}
            className="flex-1 px-4 py-2 bg-[#140342] text-white rounded-lg flex items-center justify-center gap-2"
          >
            {mode === "verify" ? (
              <ShieldCheck size={16} />
            ) : (
              <Sparkles size={16} />
            )}
            {mode === "verify" ? "Verify & Explain" : "Generate Explanation"}
          </button>
        </div>

        {/* ✅ Loader */}
        {loading && <ModalLoadingScreen />}

        {/* ✅ Response */}
        {response?.explanation && (
          <div className="bg-gray-100 p-4 rounded-lg relative mt-4">
            {mode === "verify" && response?.is_correct === false ? (
              <>
                <p className="text-red-600 font-semibold mb-1">
                  ❌ Your answer{" "}
                  <span className="underline">{claimedAnswer}</span> was
                  incorrect.
                </p>
                <p className="text-green-700 font-semibold mb-2">
                  ✅ The correct answer is{" "}
                  <span className="font-bold">{response.predicted_answer}</span>
                  .
                </p>
              </>
            ) : (
              <>
                <h4 className="text-md font-semibold mb-2 text-gray-800">
                  Predicted Answer
                </h4>
                <p className="text-lg text-[#140342] font-bold mb-2">
                  {response.predicted_answer || "N/A"}
                </p>
              </>
            )}

            <h4 className="text-md font-semibold mb-1 text-gray-800">
              Explanation
            </h4>
            <p className="text-gray-700 whitespace-pre-wrap">
              {response.explanation}
            </p>

            <button
              onClick={copyToClipboard}
              className="absolute top-2 right-2 bg-gray-300 p-1 rounded-full hover:bg-gray-400"
            >
              {copied ? (
                <FaCheckCircle className="text-green-600" />
              ) : (
                <FaCopy className="text-gray-600" />
              )}
            </button>

            {/* ✅ Clear button */}
            <div className="mt-4 flex justify-end">
              <button
                onClick={() => {
                  setQuestion("");
                  setOptions({ A: "", B: "", C: "", D: "", E: "" });
                  setClaimedAnswer("");
                  setResponse(null);
                  setCopied(false);
                }}
                className="text-sm px-4 py-2 border border-gray-400 text-gray-800 rounded-lg hover:bg-gray-200 transition"
              >
                Clear & Start Again
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MCQExplanationModal;
