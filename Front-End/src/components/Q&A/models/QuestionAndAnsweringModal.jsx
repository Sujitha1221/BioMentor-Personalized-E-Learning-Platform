import React, { useState } from "react";
import { FaFileAlt } from "react-icons/fa";
import GenerateAnswerModel from "./GenerateAnswerModel";
import CompareAnswerModel from "./CompareAnswerModel";

const QuestionAndAnsweringModal = ({ isOpen, onClose }) => {
  const [view, setView] = useState("upload");

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center p-4 z-50">
      <div className="bg-white rounded-2xl shadow-xl w-[750px] p-8 transition-all max-w-[95%] sm:p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800">
            {view === "upload"
              ? "Biology Answer Assistant"
              : view === "generate"
              ? "Create & Structure Your Answer"
              : "Compare Different Answers"}
          </h2>
          <button className="text-gray-500 hover:text-gray-700 text-xl" onClick={onClose}>
            &times;
          </button>
        </div>

        <p className="text-gray-600 mb-6 text-lg">
          {view === "upload"
            ? "Generate, evaluate, and improve your A-Level Biology answers."
            : view === "generate"
            ? "Craft precise Biology answers with proper structure."
            : "Analyze and contrast multiple Biology responses."}
        </p>

        {view === "upload" && (
          <div className="grid grid-cols-2 gap-6 sm:flex sm:flex-row sm:gap-4">
            <div
              className="border-2 border-dashed border-gray-300 p-8 sm:p-5 text-center rounded-lg cursor-pointer hover:border-gray-500 transition-all w-full sm:w-1/2"
              onClick={() => setView("generate")}
            >
              <FaFileAlt className="text-green-500 text-3xl mx-auto mb-3" />
              <p className="text-green-600 font-semibold text-lg">Generate Answer</p>
              <p className="text-sm text-gray-500 sm:hidden">Craft structured answers</p>
              <p className="hidden sm:block text-sm text-gray-500">Craft precise Biology answers with proper structure</p>
            </div>

            <div
              className="border-2 border-dashed border-gray-300 p-8 sm:p-5 text-center rounded-lg cursor-pointer hover:border-gray-500 transition-all w-full sm:w-1/2"
              onClick={() => setView("compare")}
            >
              <FaFileAlt className="text-blue-500 text-3xl mx-auto mb-3" />
              <p className="text-blue-600 font-semibold text-lg">Compare Answers</p>
              <p className="text-sm text-gray-500 sm:hidden">Analyze responses</p>
              <p className="hidden sm:block text-sm text-gray-500">Analyze and contrast multiple Biology responses</p>
            </div>
          </div>
        )}

        {view === "generate" && <GenerateAnswerModel onBack={() => setView("upload")} onClose={onClose} />}
        {view === "compare" && <CompareAnswerModel onBack={() => setView("upload")} onClose={onClose} />}
      </div>
    </div>
  );
};

export default QuestionAndAnsweringModal;
