import React, { useState, useEffect } from "react";
import QuestionAndAnsweringModal from "./models/QuestionAndAnsweringModal";
import { FcBiomass } from "react-icons/fc";
import { motion } from "framer-motion";
import LoadingScreen from "../LoadingScreen/LoadingScreen";
import logo from '../../../src/assets/Logo.png';

const QuestionAndAnsweringHomePage = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <>

      <div className="p-4 md:p-8 bg-gray-100 min-h-screen flex flex-col items-center justify-center gap-6 md:mt-5">
        {/* Q&A Generation and evaluation */}
        <div className="max-w-6xl w-full grid grid-cols-1 md:grid-cols-2 gap-12 items-center text-center md:text-left mt-5 md:mt-20">
          {/* Left Section: Text Content */}
          <div className="flex flex-col items-center md:items-start order-2 md:order-1">
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
            <motion.div
                className="mt-10 flex flex-wrap justify-center gap-4 sm:gap-6"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 0.4 }}
              >
                <motion.button
                  onClick={() => setIsModalOpen(true)}
                  className="inline-flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#140342] text-[#140342]
              font-semibold rounded-lg 
              hover:bg-[#140342] hover:text-white hover:rounded-2xl hover:shadow-lg transition-all duration-300 group"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  Open Verification Modal
                </motion.button>
              </motion.div>
            {/* <button
              className="bg-blue-600 text-white px-6 py-3 rounded-lg mt-6 hover:bg-blue-800"
              onClick={() => setIsModalOpen(true)}
            >
              Open Verification Modal
            </button> */}
            <QuestionAndAnsweringModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
          </div>

          {/* Right Section: Card */}
          <div className="hidden md:flex justify-center order-1 md:order-2">
            <div className="bg-white p-6 md:p-8 rounded-2xl shadow-lg w-64 md:w-80 text-center relative transform hover:scale-105 transition duration-300 ease-in-out">
              <img src="https://plus.unsplash.com/premium_vector-1706709710787-05e3f59294cf?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8bWVkaWNhbHxlbnwwfHwwfHx8MA%3D%3D " alt="Profile" className="w-24 h-24 mx-auto mb-4 rounded-full border-4 border-pink-500" />
              <h3 className="text-xl font-semibold">Biology AI Assistant</h3>
              <p className="text-gray-500 text-sm">Your AI-powered tutor for Sri Lankan AL Biology</p>
              <div className="flex justify-center gap-3 mt-4">
                <button className="text-green-500 text-lg">🧬</button>
                <button className="text-orange-500 text-lg">🔍</button>
              </div>
              <span className="bg-pink-500 text-white px-3 py-1 rounded-md text-xs mt-4 inline-block">AI SUPPORT</span>
              <div className="absolute -top-4 right-4 bg-gray-900 text-white p-2 rounded-full shadow-lg">
                <img src={logo} alt="Logo" className="w-7 h-7 mx-auto" />
              </div>
            </div>
          </div>
        </div>

        {/* Student Analytics Section */}
        <div className="p-4 md:p-8 bg-gray-100 flex flex-col items-center justify-center gap-6 md:mt-20">
          {/* Student Analytics Section */}
          <div className="max-w-6xl w-full grid grid-cols-1 md:grid-cols-2  gap-12 items-center text-center md:text-left">
            {/* Left Section: Analytics Card */}
            <div className="hidden md:flex justify-center md:mt-10">
              <div className="bg-white p-6 md:p-8 rounded-2xl shadow-lg w-64 md:w-80 text-center relative transform hover:scale-105 transition duration-300 ease-in-out">
                <img src="https://plus.unsplash.com/premium_vector-1682303102478-205a13e17265?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Nnx8cGVyZm9ybWFuY2V8ZW58MHx8MHx8fDA%3D"
                  alt="Student Analytics" className="w-24 h-24 mx-auto mb-4 rounded-full border-4 border-yellow-500" />

                <h3 className="text-xl font-semibold">Student Performance Analytics</h3>
                <p className="text-gray-500 text-sm">Track student progress, accuracy, and improvement over time.</p>

                <div className="flex justify-center gap-3 mt-4">
                  <button className="text-blue-500 text-lg">📊</button>
                  <button className="text-green-500 text-lg">📈</button>
                </div>

                <span className="bg-yellow-500 text-white px-3 py-1 rounded-md text-xs mt-4 inline-block">ANALYTICS REPORT</span>

                <div className="absolute -top-4 right-4 bg-gray-900 text-white p-2 rounded-full shadow-lg">
                  <img src={logo} alt="Logo" className="w-7 h-7 mx-auto" />
                </div>
              </div>
            </div>
            {/* Right Section: Card */}
            <div className="flex flex-col items-center md:items-start md:pl-6">
              <div className="p-6 bg-white rounded-full shadow-md flex items-center justify-center w-16 h-16 mb-4">
                <span className="text-3xl">📊</span>
              </div>
              <h1 className="text-4xl font-semibold">View Student Analytics</h1>
              <p className="text-gray-600 text-lg mt-4">
                Gain insights into student question-answering performance. Track accuracy, improvement trends, and areas of difficulty with detailed analytics.            </p>
              <div className="mt-4 flex gap-2 flex-wrap justify-center md:justify-start">
                {["ACCURACY RATE", "WEAK AREAS", "PROGRESS OVER TIME", "AI FEEDBACK"].map(tag => (
                  <span key={tag} className="text-sm px-3 py-1 bg-gray-200 rounded-md text-gray-700">
                    {tag}
                  </span>
                ))}
              </div>
              <motion.div
                className="mt-10 flex flex-wrap justify-center gap-4 sm:gap-6"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 0.4 }}
              >
                <motion.button
                  onClick={() => window.location.href = "http://localhost:5173/Q&A-dashboard"}
                  className="inline-flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#140342] text-[#140342]
              font-semibold rounded-lg 
              hover:bg-[#140342] hover:text-white hover:rounded-2xl hover:shadow-lg transition-all duration-300 group"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  Open Q&A Dashboard
                </motion.button>
              </motion.div>
              {/* <button
                className="bg-blue-600 text-white px-6 py-3 rounded-lg mt-6 hover:bg-blue-800"
                onClick={() => window.location.href = "http://localhost:5173/Q&A-dashboard"}
              >
                Open Q&A Dashboard
              </button> */}

              <QuestionAndAnsweringModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
            </div>
          </div>
        </div>

        {/* Q&A Answer History */}
        <div className="max-w-6xl w-full grid grid-cols-1 md:grid-cols-2 gap-12 items-center text-center md:text-left mt-5 md:mt-20">
          {/* Left Section:  Text Content */}
          <div className="flex flex-col items-center md:items-start order-2 md:order-1 md:mt-10">
            <div className="p-6 bg-white rounded-full shadow-md flex items-center justify-center w-16 h-16 mb-4">
              <span className="text-3xl">📜</span>
            </div>
            <h1 className="text-4xl font-semibold">Q&A Answer History</h1>
            <p className="text-gray-600 text-lg mt-4">
              View your previously answered questions and responses. Track your learning progress and review expert-verified answers anytime.
            </p>
            <div className="mt-4 flex gap-2 flex-wrap justify-center md:justify-start">
              {["ANSWERED QUESTIONS", "EXPERT FEEDBACK", "REVIEW HISTORY", "IMPROVEMENT TRACKING"].map(tag => (
                <span key={tag} className="text-sm px-3 py-1 bg-gray-200 rounded-md text-gray-700">
                  {tag}
                </span>
              ))}
            </div>
            <motion.div
                className="mt-10 flex flex-wrap justify-center gap-4 sm:gap-6"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 0.4 }}
              >
                <motion.button
                  onClick={() => window.location.href = "http://localhost:5173/Q&A-history"}
                  className="inline-flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#140342] text-[#140342]
              font-semibold rounded-lg 
              hover:bg-[#140342] hover:text-white hover:rounded-2xl hover:shadow-lg transition-all duration-300 group"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  View Answer History
                </motion.button>
              </motion.div>
            {/* <button
              className="bg-blue-600 text-white px-6 py-3 rounded-lg mt-6 hover:bg-blue-800"
              onClick={() => window.location.href = "http://localhost:5173/Q&A-history"}
            >
              View Answer History
            </button> */}
            <QuestionAndAnsweringModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
          </div>

          {/* Right Section: Card */}
          <div className="hidden md:flex justify-center order-1 md:order-2 md:mt-10">
            <div className="bg-white p-6 md:p-8 rounded-2xl shadow-lg w-64 md:w-80 text-center relative transform hover:scale-105 transition duration-300 ease-in-out">
              <img src="https://plus.unsplash.com/premium_vector-1683140720003-a1c000682f2b?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8YW5zd2VyfGVufDB8fDB8fHww  "
                alt="Answer History" className="w-24 h-24 mx-auto mb-4 rounded-full border-4 border-green-500" />

              <h3 className="text-xl font-semibold">Your Answer History</h3>
              <p className="text-gray-500 text-sm">Review your previously answered questions anytime.</p>

              <div className="flex justify-center gap-3 mt-4">
                <button className="text-green-500 text-lg">📜</button>
                <button className="text-orange-500 text-lg">🔍</button>
              </div>

              <span className="bg-green-500 text-white px-3 py-1 rounded-md text-xs mt-4 inline-block">Q&A HISTORY</span>

              <div className="absolute -top-4 right-4 bg-gray-900 text-white p-2 rounded-full shadow-lg">
                <img src={logo} alt="Logo" className="w-7 h-7 mx-auto" />
              </div>
            </div>
          </div>
        </div>

        {/* Personalized Learning Assistance */}
        <div className="p-4 md:p-8 bg-gray-100 flex flex-col items-center justify-center gap-6 md:mt-20">
          {/* Student Analytics Section */}
          <div className="max-w-6xl w-full grid grid-cols-1 md:grid-cols-2  gap-12 items-center text-center md:text-left">
            {/* Left Section: Analytics Card */}
            <div className="hidden md:flex justify-center md:mt-10">
              <div className="bg-white p-6 md:p-8 rounded-2xl shadow-lg w-64 md:w-80 text-center relative transform hover:scale-105 transition duration-300 ease-in-out">
                <img src="https://images.unsplash.com/vector-1739026151896-fb077bba7a70?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8c3R1ZHklMjBtZXRyaWFsc3xlbnwwfHwwfHx8MA%3D%3D" alt="Profile" className="w-24 h-24 mx-auto mb-4 rounded-full border-4 border-gray-500" />
                <h3 className="text-xl font-semibold">Smart Study Guide</h3>
                <p className="text-gray-500 text-sm">BioMentor recommends AL Biology notes based on your performance, helping you focus on weak areas.</p>
                <div className="flex justify-center gap-3 mt-4">
                  <button className="text-green-500 text-lg">📖</button>
                  <button className="text-orange-500 text-lg">✅</button>
                </div>
                <span className="bg-gray-500 text-white px-3 py-1 rounded-md text-xs mt-4 inline-block">PERFORMANCE-BASED STUDY</span>
                <div className="absolute -top-4 right-4 bg-gray-900 text-white p-2 rounded-full shadow-lg">
                  <img src={logo} alt="Logo" className="w-7 h-7 mx-auto" />
                </div>
              </div>
            </div>
            {/* Right Section: Card */}
            <div className="flex flex-col items-center md:items-start order-2 md:order-1">
              <div className="p-6 bg-white rounded-full shadow-md flex items-center justify-center w-16 h-16 mb-4">
                <span className="text-3xl">📘</span>
              </div>
              <h1 className="text-4xl font-semibold">Personalized Study Recommendations with BioMentor</h1>
              <p className="text-gray-600 text-lg mt-4">
                Based on your performance, BioMentor intelligently recommends notes and study materials from the Sri Lankan AL Biology resource book, ensuring you focus on areas that need improvement.
              </p>
              <div className="mt-4 flex gap-2 flex-wrap justify-center md:justify-start">
                {["SMART NOTES", "TOPIC TIPS", "GUIDED STUDY", "CONCEPT BOOST", "EXAM PREP"].map(tag => (
                  <span key={tag} className="text-sm px-3 py-1 bg-gray-200 rounded-md text-gray-700">
                    {tag}
                  </span>
                ))}
              </div>
              <motion.div
                className="mt-10 flex flex-wrap justify-center gap-4 sm:gap-6"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 0.4 }}
              >
                <motion.button
                  onClick={() => window.location.href = "http://localhost:5173/Q&A-materials"}
                  className="inline-flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#140342] text-[#140342]
              font-semibold rounded-lg 
              hover:bg-[#140342] hover:text-white hover:rounded-2xl hover:shadow-lg transition-all duration-300 group"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  Get Your Study Plan
                </motion.button>
              </motion.div>
              {/* <button
                className="bg-indigo-600 text-white px-6 py-3 rounded-lg mt-6 hover:bg-indigo-800"
                onClick={() => window.location.href = "http://localhost:5173/Q&A-materials"}
              >
                Get Your Study Plan
              </button> */}
              <QuestionAndAnsweringModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default QuestionAndAnsweringHomePage;
