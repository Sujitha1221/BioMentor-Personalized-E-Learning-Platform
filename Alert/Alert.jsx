import React, { useEffect } from "react";
import { FaTimesCircle } from "react-icons/fa";

const AlertMessage = ({ message, type = "error", onClose }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 3000); // Auto-close after 3 seconds

    return () => clearTimeout(timer);
  }, [onClose]);

  if (!message) return null;

  // Define background color based on the alert type
  const bgColor =
    type === "error"
      ? "bg-red-500"
      : type === "success"
      ? "bg-green-500"
      : "bg-yellow-500"; // Warning color

  return (
    <div
      className={`fixed top-5 right-5 p-4 rounded-lg shadow-lg text-white z-50 flex items-center gap-3 ${bgColor}`}
    >
      <FaTimesCircle size={20} />
      <span>{message}</span>
      <button onClick={onClose} className="ml-2 text-white">
        ✖
      </button>
    </div>
  );
};

export default AlertMessage;
