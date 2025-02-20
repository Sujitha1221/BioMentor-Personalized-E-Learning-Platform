import React, { useState } from "react";
import axios from "axios";
import ReactLoading from "react-loading";
import ComparisonModal from "./ComparisonModal";
import { FaTimesCircle } from "react-icons/fa";
import { ArrowLeft, CheckCircle } from "lucide-react";

const CompareAnswerModel = ({ onBack }) => {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [answerType, setAnswerType] = useState("structured");
  const [feedback, setFeedback] = useState(null);
  const [modelAnswer, setModelAnswer] = useState("");
  const [relatedWebsites, setRelatedWebsites] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);

  const handleCompareAnswer = async () => {
    if (!question || !answer || !answerType) {
      alert("Please fill out all fields before comparing.");
      return;
    }

    setLoading(true);
    setFeedback(null);
    setModelAnswer("");
    setRelatedWebsites([]);

    try {
      const response = await axios.post("http://127.0.0.1:8000/evaluate-answer", {
        question,
        user_answer: answer,
        question_type: answerType,
      });

      setFeedback(response.data.evaluation_result);
      setModelAnswer(response.data.model_answer);
      setRelatedWebsites(response.data.related_websites || []);

      setShowModal(true);
    } catch (error) {
      console.error("Error comparing answer:", error);
      alert("Failed to compare answer. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-5">
      <div className="bg-gray-100 p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Compare Answer</h3>

        <div className="mb-4">
          <label className="block text-gray-700 font-medium mb-2">Question</label>
          <input
            type="text"
            placeholder="Enter your question..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            disabled={loading}
            className="w-full border border-gray-300 p-3 rounded-lg focus:ring-2 focus:ring-blue-400 disabled:opacity-50"
          />
        </div>

        <div className="mb-4">
          <label className="block text-gray-700 font-medium mb-2">Answer Type</label>
          <select
            value={answerType}
            onChange={(e) => setAnswerType(e.target.value)}
            disabled={loading}
            className="w-full border border-gray-300 p-3 rounded-lg bg-white focus:ring-2 focus:ring-blue-400 disabled:opacity-50"
          >
            <option value="structured">Structured</option>
            <option value="essay">Essay</option>
          </select>
        </div>

        <div className="mb-4">
          <label className="block text-gray-700 font-medium mb-2">Your Answer</label>
          <textarea
            placeholder="Enter your answer..."
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            disabled={loading}
            className="w-full border border-gray-300 p-3 rounded-lg h-24 resize-none focus:ring-2 focus:ring-blue-400 disabled:opacity-50"
          ></textarea>
        </div>

        {loading && (
          <div className="flex justify-center mt-4">
            <ReactLoading type="spin" color="#4f46e5" height={40} width={40} />
          </div>
        )}

        <div className="flex justify-between mt-4">
          <button
            className="inline-flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#140342] text-white bg-[#140342] font-semibold rounded-lg 
    transition-transform duration-300 hover:scale-105 hover:bg-[#32265a]"
            onClick={onBack}
            disabled={loading}
          >
            <ArrowLeft size={20} /> Back
          </button>

          <button
            onClick={handleCompareAnswer}
            disabled={loading}
            className="inline-flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#00FF84] text-[#140342] bg-[#00FF84] font-semibold rounded-lg 
    transition-transform duration-300 hover:scale-105 hover:bg-[#00cc70]"
          >
            <CheckCircle size={20} /> Compare Answer
          </button>

        </div>
      </div>

      <ComparisonModal
        showModal={showModal}
        loading={loading}
        feedback={feedback}
        modelAnswer={modelAnswer}
        answer={answer}
        relatedWebsites={relatedWebsites}
        onClose={() => setShowModal(false)}
      />
    </div>
  );
};

export default CompareAnswerModel;