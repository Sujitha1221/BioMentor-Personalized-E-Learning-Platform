import React from "react";
import { Sparkles, ShieldCheck, X } from "lucide-react";

const MCQExplanationSelectorModal = ({ onSelect, onClose }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-30 flex justify-center items-center p-4 z-50">
      <div className="bg-white rounded-2xl shadow-xl w-[600px] p-8 max-w-[95%] sm:p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800">MCQ Explanation</h2>
          <button className="text-gray-500 hover:text-gray-700 text-xl" onClick={onClose}>
            <X />
          </button>
        </div>

        <p className="text-gray-600 mb-6">
          What would you like to do with your MCQ? Choose whether to generate a clear explanation or check if a chosen answer is correct.
        </p>

        <div className="grid grid-cols-2 gap-6">
          <button
            className="border-2 border-dashed border-gray-300 p-6 rounded-lg hover:border-blue-500"
            onClick={() => onSelect("explain")}
          >
            <Sparkles className="text-blue-500 mx-auto mb-2" />
            <p className="text-blue-700 font-semibold text-lg text-center">Generate Explanation</p>
          </button>

          <button
            className="border-2 border-dashed border-gray-300 p-6 rounded-lg hover:border-green-500"
            onClick={() => onSelect("verify")}
          >
            <ShieldCheck className="text-green-500 mx-auto mb-2" />
            <p className="text-green-700 font-semibold text-lg text-center">Check Answer & Explain</p>
          </button>
        </div>
      </div>
    </div>
  );
};

export default MCQExplanationSelectorModal;
