import React from "react";
import { motion } from "framer-motion";

const RetryQuizModal = ({ isOpen, onClose, onConfirm }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
      <motion.div
        className="bg-white rounded-2xl shadow-xl p-6 max-w-lg w-full text-center"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <h2 className="text-3xl font-bold text-gray-800">🎉 All the Best!</h2>
        <p className="text-gray-600 text-lg mt-4">
          This attempt will not affect your performance, but you can practice
          and improve your knowledge.🎯🔥
        </p>

        <div className="mt-6 flex justify-center gap-4">
          <button
            onClick={onClose}
            className="px-6 py-3 bg-gray-400 text-white text-lg font-semibold rounded-lg shadow-md hover:bg-gray-500 transition"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className="px-6 py-3 bg-green-600 text-white text-lg font-semibold rounded-lg shadow-md hover:bg-green-700 transition"
          >
            Start Quiz
          </button>
        </div>
      </motion.div>
    </div>
  );
};

export default RetryQuizModal;
