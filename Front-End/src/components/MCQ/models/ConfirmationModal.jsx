import React from "react";

const ConfirmationModal = ({
  isOpen,
  onClose,
  onConfirm,
  hasUnanswered,
  isSubmitting,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center">
      <div className="bg-white p-6 rounded-lg shadow-lg text-center">
        <h2 className="text-xl font-bold text-gray-800">
          {hasUnanswered ? "Unanswered Questions" : "Confirm Submission"}
        </h2>
        <p className="text-gray-600 mt-2">
          {hasUnanswered
            ? "You haven't answered all questions. Are you sure you want to submit?"
            : "Are you sure you want to submit the quiz?"}
        </p>
        <div className="mt-4 flex justify-center gap-4">
          <button
            onClick={onClose}
            className="px-5 py-2 bg-gray-500 text-white rounded-lg"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className="px-5 py-2 bg-green-500 text-white rounded-lg"
          >
            {isSubmitting ? "Submitting..." : "Submit"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmationModal;
