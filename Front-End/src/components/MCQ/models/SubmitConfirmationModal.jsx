import React from "react";
import { motion } from "framer-motion";

const SubmitConfirmationModal = ({ isOpen, onClose, onConfirm }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
      <motion.div
        className="bg-white rounded-2xl shadow-xl p-6 max-w-lg w-full text-center"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <h2 className="text-2xl font-bold text-gray-800">
          ⚠️ Confirm Submission
        </h2>
        <p className="text-gray-600 text-lg mt-4">
          Are you sure you want to submit? Once submitted, you{" "}
          <span className="font-bold text-red-600">cannot revert</span>.
        </p>

        <div className="mt-6 flex justify-center gap-4">
          <button
            onClick={onConfirm}
            className="px-6 py-3 bg-red-600 text-white text-lg font-semibold rounded-lg shadow-md hover:bg-red-700 transition"
          >
            Yes, Submit
          </button>
          <button
            onClick={onClose}
            className="px-6 py-3 bg-gray-400 text-white text-lg font-semibold rounded-lg shadow-md hover:bg-gray-500 transition"
          >
            Cancel
          </button>
        </div>
      </motion.div>
    </div>
  );
};

export default SubmitConfirmationModal;
