import React, { useState } from "react";
import QuestionAndAnsweringModal from "./models/QuestionAndAnsweringModal";
import { FcBiomass } from "react-icons/fc";

const QuestionAndAnsweringHomePage = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <div className="p-4 md:p-8 bg-gray-100 min-h-screen flex items-center justify-center">
      <div className="max-w-6xl w-full flex flex-col md:flex-row items-center justify-center gap-12">
        {/* Left Section: Text Content */}
        <div className="flex-1 flex flex-col items-center md:items-start text-center md:text-left">
          <div className="p-6 bg-white rounded-full shadow-md flex items-center justify-center w-16 h-16 mb-4">
            <span className="text-3xl">🔬</span>
          </div>
          <h1 className="text-4xl font-semibold">Structured and Essay Type Question Assistance</h1>
          <p className="text-gray-600 text-lg mt-4">
            Need help with structured and essay-type questions? Generate accurate answers or compare your answers with expert solutions to get personalized feedback.
          </p>
          <div className="mt-4 flex gap-2 flex-wrap justify-center md:justify-start">
            {["MODEL ANSWER", "FEEDBACK SYSTEM", "QUESTION BANK", "BIOLOGY TOPICS", "EXAM GUIDES"].map(tag => (
              <span key={tag} className="text-sm px-3 py-1 bg-gray-200 rounded-md text-gray-700">
                {tag}
              </span>
            ))}
          </div>
          <button
            className="bg-blue-600 text-white px-6 py-3 rounded-lg mt-6 hover:bg-blue-800"
            onClick={() => setIsModalOpen(true)}
          >
            Open Verification Modal
          </button>
          <QuestionAndAnsweringModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
        </div>

        {/* Right Section: One Beautiful Card */}
        <div className="flex-1 flex justify-center items-center">
          <div className="bg-white p-8 rounded-2xl shadow-lg w-80 text-center relative transform hover:scale-105 transition duration-300 ease-in-out">
            <img src="https://plus.unsplash.com/premium_photo-1681487546184-98bd8bacc20a?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D" alt="Profile" className="w-24 h-24 mx-auto mb-4 rounded-full border-4 border-blue-500" />
            <h3 className="text-xl font-semibold">Biology AI Assistant</h3>
            <p className="text-gray-500 text-sm">Your AI-powered tutor for Sri Lankan AL Biology</p>
            <div className="flex justify-center gap-3 mt-4">
              <button className="text-green-500 text-lg">🧬</button>
              <button className="text-orange-500 text-lg">🔍</button>
            </div>
            <span className="bg-pink-500 text-white px-3 py-1 rounded-md text-xs mt-4 inline-block">AI SUPPORT</span>
            <div className="absolute -top-4 right-4 bg-gray-900 text-white p-2 rounded-full shadow-lg">
              <FcBiomass className="text-lg" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuestionAndAnsweringHomePage;
