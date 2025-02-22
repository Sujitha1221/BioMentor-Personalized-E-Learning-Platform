import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FaArrowLeft, FaArrowRight } from "react-icons/fa";
import {
  FiInfo,
  FiCheck,
  FiAward,
  FiThumbsUp,
  FiVolume2,
  FiSliders,
} from "react-icons/fi";
import extractImg from "../../assets/image/extract.jpg";
import summaryImg from "../../assets/image/summary.jpg";
import topicImg from "../../assets/image/topic.jpeg";
import TopicSummaryModal from "./TopicSummaryModal";

// Slide data for the slideshow
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

// Feature items data with larger icons
const features = [
  {
    icon: <FiInfo className="text-blue-500 mr-2 w-10 h-10" />,
    label: "Enter Topic",
    desc: "Type in any biology topic you need help with.",
  },
  {
    icon: <FiCheck className="text-green-500 mr-2 w-10 h-10" />,
    label: "Extract Details",
    desc: "Retrieve essential points, key concepts, and explanations from curated resources.",
  },
  {
    icon: <FiAward className="text-purple-500 mr-2 w-10 h-10" />,
    label: "Detailed Summary",
    desc: "Receive a comprehensive summary covering all important aspects.",
  },
  {
    icon: <FiThumbsUp className="text-orange-500 mr-2 w-10 h-10" />,
    label: "Study Efficiently",
    desc: "Boost your study sessions with concise, accurate information.",
  },
  {
    icon: <FiVolume2 className="text-red-500 mr-2 w-10 h-10" />,
    label: "Audible Summary",
    desc: "Listen to the summary for a hands-free learning experience.",
  },
  {
    icon: <FiSliders className="text-teal-500 mr-2 w-10 h-10" />,
    label: "Customizable Length",
    desc: "Adjust the summary length with customizable word count options.",
  },
];

// Component for individual feature item
const FeatureItem = ({ icon, label, desc }) => (
  <div className="flex items-start space-x-2">
    {icon}
    <div>
      <p className="font-semibold">{label}</p>
      <p className="text-gray-600 text-sm">{desc}</p>
    </div>
  </div>
);

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
    <section className="relative flex flex-col gap-8 bg-gray-100 sm:flex-row sm:gap-x-16 items-center justify-between px-6 sm:px-20 py-16 max-w-7xl mx-auto">
      {/* Left Section - Heading, Feature Items & Button */}
      <div className="w-full sm:w-1/2 flex flex-col items-center sm:items-start text-center sm:text-left">
        <h2 className="text-3xl font-bold text-[#140342]">
          Summarize Any Biology Topic Instantly
        </h2>
        {/* Two-column grid for features */}
        <div className="mt-4 grid grid-cols-2 gap-4">
          {features.map((feature, index) => (
            <FeatureItem
              key={index}
              icon={feature.icon}
              label={feature.label}
              desc={feature.desc}
            />
          ))}
        </div>
        <motion.div
          className="mt-6"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <motion.button
            onClick={() => setIsModalOpen(true)}
            className="px-6 py-3 border-2 border-[#140342] text-[#140342] font-semibold rounded-lg hover:bg-[#140342] hover:text-white hover:rounded-2xl hover:shadow-lg transition-all duration-300 group"
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
      {/* Topic Summary Modal */}
      <TopicSummaryModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </section>
  );
};

export default TopicSummary;
