import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FaArrowLeft, FaArrowRight } from "react-icons/fa";
import extractImg from "../../assets/image/extract.jpg";
import summaryImg from "../../assets/image/summary.jpg";
import topicImg from "../../assets/image/topic.jpeg";
import TopicSummaryModal from "./TopicSummaryModal";

const slides = [
  {
    id: 1,
    title: "1. Enter Topic",
    image: topicImg,
    bgColor: "#D9E3F0",
    textColor: "#140342",
  },
  {
    id: 2,
    title: "2. Extract Relevant Content",
    image: extractImg,
    bgColor: "#C1D3FE",
    textColor: "#0057D9",
  },
  {
    id: 3,
    title: "3. Generate Summary",
    image: summaryImg,
    bgColor: "#B0E0E6",
    textColor: "#009688",
  },
];

const TopicSummary = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [currentSlide, setCurrentSlide] = useState(0);

  // Auto-slide every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % slides.length);
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <section className="relative flex flex-col bg-gray-100 sm:flex-row items-center justify-between px-6 sm:px-20 py-16 bg-gray-100 max-w-7xl mx-auto">
      {/* Left Section - Text & Button */}
      <div className="w-full sm:w-1/2 flex flex-col items-center sm:items-start text-center sm:text-left">
        <h2 className="text-3xl font-bold text-[#140342]">
          Summarize Any Biology Topic Instantly
        </h2>
        <p className="text-gray-600 mt-4 text-sm leading-relaxed">
          Enter any biology topic, and our tool will extract{" "}
          <b>all essential points, key concepts, and explanations</b> from{" "}
          <b>approved educational resources</b>. It ensures a{" "}
          <b>comprehensive and detailed summary</b>, covering all important
          aspects without missing critical information, helping you study
          efficiently.
        </p>

        {/* Start Summarizing Button */}
        <motion.div
          className="mt-6"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <motion.button
            onClick={() => setIsModalOpen(true)}
            className="px-6 py-3 border-2 border-[#140342] text-[#140342] font-semibold rounded-lg 
            hover:bg-[#140342] hover:text-white hover:rounded-2xl hover:shadow-lg transition-all duration-300 group"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Start Summarizing
          </motion.button>
        </motion.div>
      </div>

      {/* Right Section - Slideshow */}
      <div className="relative w-full sm:w-1/2 flex justify-center sm:justify-end items-center mt-10 sm:mt-0">
        <div className="relative w-[400px] sm:w-[500px] h-auto">
          <AnimatePresence mode="wait">
            <motion.div
              key={slides[currentSlide].id}
              className="p-8 rounded-xl shadow-lg flex flex-col items-center text-center w-full"
              style={{
                backgroundColor: slides[currentSlide].bgColor,
                color: slides[currentSlide].textColor,
              }}
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              transition={{ duration: 0.5 }}
            >
              <img
                src={slides[currentSlide].image}
                alt={slides[currentSlide].title}
                className="w-72 sm:w-80 h-auto rounded-lg shadow-md"
              />
              <p className="text-lg font-bold mt-3">
                {slides[currentSlide].title}
              </p>
            </motion.div>
          </AnimatePresence>

          {/* Navigation Buttons */}
          <div className="absolute top-1/2 left-0 -translate-y-1/2 flex justify-between w-full px-4">
            <button
              onClick={() =>
                setCurrentSlide((prev) =>
                  prev === 0 ? slides.length - 1 : prev - 1
                )
              }
              className="p-3 bg-white rounded-full shadow-lg text-gray-700 hover:bg-gray-200 transition"
            >
              <FaArrowLeft />
            </button>
            <button
              onClick={() =>
                setCurrentSlide((prev) => (prev + 1) % slides.length)
              }
              className="p-3 bg-white rounded-full shadow-lg text-gray-700 hover:bg-gray-200 transition"
            >
              <FaArrowRight />
            </button>
          </div>

          {/* Dots Indicator */}
          <div className="flex justify-center mt-3 space-x-2">
            {slides.map((_, index) => (
              <div
                key={index}
                className={`h-3 w-3 rounded-full ${
                  currentSlide === index ? "bg-[#140342]" : "bg-gray-300"
                }`}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Import TopicModal and Pass State */}
      <TopicSummaryModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </section>
  );
};

export default TopicSummary;
