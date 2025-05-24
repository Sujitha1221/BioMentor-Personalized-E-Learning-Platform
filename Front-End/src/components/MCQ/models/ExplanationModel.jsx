import React, { useState } from "react";
import { motion } from "framer-motion";

const ExplainModal = ({ isOpen, onClose, explanation, verifiedAnswer, loading }) => {
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const handleCopy = () => {
    const text = `✅ Verified Answer: ${verifiedAnswer || "N/A"}\n\n${explanation}`;
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500); // Reset after 1.5 seconds
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 20 }}
        transition={{ duration: 0.4 }}
        className="bg-white rounded-xl shadow-2xl p-6 max-w-lg w-full"
      >
        <h2 className="text-xl font-bold mb-4">😁Verified Explanation</h2>

        {loading ? (
          <p className="text-gray-600">😃Generating explanation...</p>
        ) : (
          <>
            {verifiedAnswer && (
              <p className="text-green-700 font-semibold mb-2">
                ✅ Verified Answer: <span className="font-bold">{verifiedAnswer}</span>
              </p>
            )}
            <p className="text-gray-800 whitespace-pre-wrap">{explanation}</p>
          </>
        )}

        {/* Buttons */}
        <div className="mt-6 flex justify-between items-center">
          <button
            className="px-4 py-2 bg-[#140342] text-white rounded-lg hover:bg-[#140342]"
            onClick={onClose}
          >
            Close
          </button>
          <button
            className={`px-4 py-2 rounded-lg font-medium transition ${
              copied ? "bg-green-500 text-white" : "bg-gray-200 text-gray-800 hover:bg-gray-300"
            }`}
            onClick={handleCopy}
          >
            {copied ? "Copied!" : "Copy"}
          </button>
        </div>
      </motion.div>
    </div>
  );
};

export default ExplainModal;
