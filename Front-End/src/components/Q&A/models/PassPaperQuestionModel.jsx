import React, { useEffect, useState } from "react";
import { Tab } from "@headlessui/react";
import { XIcon } from "lucide-react";
import ComparisonModal from "./ComparisonModal";

const PassPaperQuestionModel = ({ isOpen, onClose, studentId }) => {
  const [questions, setQuestions] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [answers, setAnswers] = useState({ structured: "", essay: "" });
  const [showComparisonModal, setShowComparisonModal] = useState(false);
  const [evaluationResult, setEvaluationResult] = useState(null);
  const [submissionStatus, setSubmissionStatus] = useState("");

  useEffect(() => {
    if (!isOpen) return;

    const fetchQuestions = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:8000/get-student-question/${studentId}`);
        if (!response.ok) {
          throw new Error("Failed to fetch questions");
        }
        const data = await response.json();
        setQuestions(data.questions);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchQuestions();
  }, [studentId, isOpen]);

  const handleSubmit = async (questionType, question, answer) => {
    if (!answer.trim()) {
      setSubmissionStatus("Please enter an answer before submitting.");
      return;
    }

    try {
      setSubmissionStatus("Submitting...");
      const response = await fetch("http://127.0.0.1:8000/evaluate-passpaper-answer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          student_id: "1234",
          question,
          user_answer: answer,
          question_type: questionType,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to evaluate answer");
      }
      const data = await response.json();
      setEvaluationResult(data);
      setShowComparisonModal(true);
      setSubmissionStatus("Answer submitted successfully!");
    } catch (error) {
      console.error("Error evaluating answer:", error);
      setSubmissionStatus("Failed to submit answer. Try again.");
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
      <div className="bg-white p-6 rounded-lg shadow-xl max-w-2xl w-full relative">
        
        {/* Close Button */}
        <button onClick={onClose} className="absolute top-3 right-3 text-gray-500 hover:text-gray-700 text-xl">
          <XIcon className="w-6 h-6" />
        </button>

        <h3 className="text-2xl font-bold text-[#140342] mb-4 text-center">Assigned Questions</h3>

        {loading ? (
          <div className="text-center text-gray-600">Loading questions...</div>
        ) : error ? (
          <div className="text-center text-red-500">Error: {error}</div>
        ) : (
          <Tab.Group>
            {/* Tabs */}
            <Tab.List className="flex mb-4 border-b">
              <Tab className={({ selected }) =>
                selected
                  ? "px-4 py-2 w-1/2 text-lg font-semibold text-[#140342] border-b-2 border-[#140342]"
                  : "px-4 py-2 w-1/2 text-lg font-semibold text-gray-500"
              }>
                Structured
              </Tab>
              <Tab className={({ selected }) =>
                selected
                  ? "px-4 py-2 w-1/2 text-lg font-semibold text-[#140342] border-b-2 border-[#140342]"
                  : "px-4 py-2 w-1/2 text-lg font-semibold text-gray-500"
              }>
                Essay
              </Tab>
            </Tab.List>

            {/* Panels */}
            <Tab.Panels>
              
              {/* Structured Question Panel */}
              <Tab.Panel className="p-4 bg-gray-100 rounded-lg shadow-inner">
                <h4 className="text-lg font-semibold text-gray-700">Structured Question</h4>
                <p className="text-gray-600 mt-2 bg-white p-4 rounded-lg shadow-md border border-gray-200">
                  <span className="font-medium">Q:</span> {questions.Structured_Question.Question}
                </p>
                <textarea
                  className="w-full border border-gray-300 p-3 rounded-lg mt-2 focus:border-[#140342] focus:ring-[#140342] shadow-sm"
                  placeholder="Enter your answer..."
                  value={answers.structured}
                  onChange={(e) => setAnswers({ ...answers, structured: e.target.value })}
                />
                <div className="flex justify-center mt-4">
                  <button
                    onClick={() => handleSubmit("structured", questions.Structured_Question.Question, answers.structured)}
                    disabled={!answers.structured.trim()}
                    className="bg-[#00FF84] text-[#140342] px-6 py-3 rounded-lg font-semibold transition-transform duration-300 hover:scale-105 hover:bg-[#00cc70] disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Submit Answer
                  </button>
                </div>
              </Tab.Panel>

              {/* Essay Question Panel */}
              <Tab.Panel className="p-4 bg-gray-100 rounded-lg shadow-inner">
                <h4 className="text-lg font-semibold text-gray-700">Essay Question</h4>
                <p className="text-gray-600 mt-2 bg-white p-4 rounded-lg shadow-md border border-gray-200">
                  <span className="font-medium">Q:</span> {questions.Essay_Question.Question}
                </p>
                <textarea
                  className="w-full border border-gray-300 p-3 rounded-lg mt-2 focus:border-[#140342] focus:ring-[#140342] shadow-sm"
                  placeholder="Enter your answer..."
                  value={answers.essay}
                  onChange={(e) => setAnswers({ ...answers, essay: e.target.value })}
                />
                <div className="flex justify-center mt-4">
                  <button
                    onClick={() => handleSubmit("essay", questions.Essay_Question.Question, answers.essay)}
                    disabled={!answers.essay.trim()}
                    className="bg-[#00FF84] text-[#140342] px-6 py-3 rounded-lg font-semibold transition-transform duration-300 hover:scale-105 hover:bg-[#00cc70] disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Submit Answer
                  </button>
                </div>
              </Tab.Panel>

            </Tab.Panels>
          </Tab.Group>
        )}

        {/* Submission Status */}
        {submissionStatus && (
          <p className="text-center text-sm text-gray-600 mt-3">{submissionStatus}</p>
        )}
      </div>

      {/* Comparison Modal */}
      {showComparisonModal && evaluationResult && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
          <ComparisonModal
            showModal={showComparisonModal}
            loading={false}
            feedback={evaluationResult.evaluation_result}
            modelAnswer={evaluationResult.model_answer}
            answer={evaluationResult.user_answer}
            relatedWebsites={evaluationResult.related_websites}
            onClose={() => setShowComparisonModal(false)}
          />
        </div>
      )}
    </div>
  );
};

export default PassPaperQuestionModel;
