import React, { useState } from "react";
import { motion } from "framer-motion";
import extractImg from "../../assets/image/extract.jpg";
import summaryImg from "../../assets/image/summary.png";
import topicImg from "../../assets/image/topic.jpeg";
import TopicSummaryModal from "./TopicSummaryModal";

const TopicSummary = () => {
  const [isModalOpen, setIsModalOpen] = useState(false); // Modal state

  return (
    <section className="relative flex flex-col sm:flex-row items-center justify-between px-6 sm:px-20 py-16 bg-gray-100 max-w-7xl mx-auto">
      {/* Left Section - Text & Button */}
      <div className="w-full sm:w-1/2 flex flex-col items-center sm:items-start text-center sm:text-left">
        <h2 className="text-3xl font-bold">
          Summarize Any Biology Topic Instantly
        </h2>
        <p className="text-gray-600 mt-4 text-sm">
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
            onClick={() => setIsModalOpen(true)} // Open modal
            className="px-6 py-3 border-2 border-[#140342] text-[#140342] font-semibold rounded-lg 
            hover:bg-[#140342] hover:text-white hover:rounded-2xl hover:shadow-lg transition-all duration-300 group"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Start Summarizing
          </motion.button>
        </motion.div>
      </div>

     {/* Right Section - Responsive Layout for Images */}
<div className="relative w-full sm:w-1/2 flex justify-center sm:justify-end items-center mt-6 sm:mt-4">
  <div className="flex flex-col sm:grid sm:grid-cols-2 gap-4 sm:gap-6 items-center sm:items-start w-full sm:w-[500px]">
    
    {/* Step 1 - Topic Selection */}
    <motion.div
      className="bg-slate-500 p-4 rounded-xl shadow-lg w-64 sm:w-64 transition-transform duration-300 hover:scale-110"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.1 }} // Zoom-in effect
      transition={{ duration: 0.6, delay: 0.1 }}
    >
      <img
        src={topicImg}
        alt="Topic Selection"
        className="w-full rounded-lg shadow-md"
      />
      <p className="text-md font-bold mt-3 text-black text-center tracking-wide">
        1. Enter Topic
      </p>
    </motion.div>

    {/* Step 2 - Extracting Information */}
    <motion.div
      className="bg-[#140342] p-4 rounded-xl shadow-lg w-64 sm:w-64 transition-transform duration-300 hover:scale-110"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.1 }} // Zoom-in effect
      transition={{ duration: 0.6, delay: 0.3 }}
    >
      <img
        src={extractImg}
        alt="Extracting Information"
        className="w-full rounded-lg shadow-md"
      />
      <p className="text-md font-bold mt-3 text-white text-center tracking-wide">
        2. Extract Relevant Content
      </p>
    </motion.div>

    {/* Step 3 - Summarization */}
    <motion.div
      className="bg-[#64B5F6] p-4 rounded-xl shadow-lg w-64 sm:w-72 relative col-span-2 flex flex-col items-center sm:justify-center mx-auto mt-3 sm:mt-2 transition-transform duration-300 hover:scale-110"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.1 }} // Zoom-in effect
      transition={{ duration: 0.6, delay: 0.5 }}
    >
      <img
        src={summaryImg}
        alt="Summarizing Output"
        className="w-48 rounded-lg shadow-md"
      />
      <p className="text-md font-bold mt-3 text-black text-center tracking-wide">
        3. Generate Summary
      </p>
    </motion.div>
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
