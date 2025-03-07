import React, { useEffect } from "react";
import {
  FaTimesCircle,
  FaCheckCircle,
  FaExclamationCircle,
} from "react-icons/fa";
import { MdClose } from "react-icons/md"; // Close button icon

const AlertMessage = ({ message, type = "error", onClose }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 3000); // Auto-close after 3 seconds

    return () => clearTimeout(timer);
  }, [onClose]);

  if (!message) return null;

  // Define styles based on alert type
  const alertStyles = {
    error: { bgColor: "bg-red-500", Icon: FaTimesCircle },
    success: { bgColor: "bg-green-500", Icon: FaCheckCircle },
    warning: { bgColor: "bg-yellow-400", Icon: FaExclamationCircle },
  };

  const { bgColor, Icon } = alertStyles[type] || alertStyles.error; // Default to error

  return (
    <div
      className={`fixed top-5 right-5 p-4 rounded-lg shadow-lg text-white z-50 flex items-center gap-3 ${bgColor}`}
    >
      <Icon size={20} /> {/* Dynamic icon based on alert type */}
      <span>{message}</span>
      <button onClick={onClose} className="ml-2 text-white hover:text-gray-300">
        <MdClose size={22} /> {/* Close button */}
      </button>
    </div>
  );
};

export default AlertMessage;