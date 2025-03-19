import React from "react";
import { FaWhatsapp, FaFacebook, FaInstagram, FaEnvelope } from "react-icons/fa";
import { MdOutlineClose } from "react-icons/md";

const SharingModal = ({ isOpen, onClose, score }) => {
  if (!isOpen) return null;

  const message = `I just scored ${score} points in Vocabulary Mastery in BioMentor! Can you beat my score? 🏆`;

  const shareLinks = {
    whatsapp: `https://wa.me/?text=${encodeURIComponent(message)}`,
    email: `mailto:?subject=My%20Vocabulary%20Mastery%20Score!&body=${encodeURIComponent(message)}`,
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl w-[500px] p-6 text-center relative">
        <button onClick={onClose} className="absolute right-4 top-4 text-gray-500 hover:text-gray-700">
          <MdOutlineClose size={24} />
        </button>

        <h2 className="text-2xl font-bold text-gray-800 mb-4">Quiz Completed!</h2>
        <p className="text-lg font-semibold">Your Score: {score}</p>

        <div className="flex justify-center gap-6 mt-4">
          <FaWhatsapp size={40} className="text-green-500 cursor-pointer" onClick={() => window.open(shareLinks.whatsapp, "_blank")} />
          <FaEnvelope size={40} className="text-gray-700 cursor-pointer" onClick={() => window.open(shareLinks.email, "_blank")} />
        </div>
      </div>
    </div>
  );
};

export default SharingModal;
