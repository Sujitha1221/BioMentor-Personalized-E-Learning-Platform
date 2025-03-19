import React from "react";
import { motion } from "framer-motion";
import { RocketLaunchIcon } from "@heroicons/react/24/outline";

import vocabularyImage from "../../assets/image/vocabulary-image.png";

const Hero = ({ scrollToSummarize }) => {
  return (
    <section className="relative h-screen flex flex-col items-center justify-center text-white overflow-hidden bg-[#140342] px-4 sm:px-6">
      {/* Animated Logo */}
      <motion.img
        src={vocabularyImage}
        alt="Vocabulary image"
        className="h-40 sm:h-48 mt-4 sm:mt-20 mb-2 sm:mb-6"
        animate={{ x: [0, -3, 3, -3, 3, 0], rotate: [0, -2, 2, -2, 2, 0] }}
        transition={{ duration: 1.2, repeat: Infinity, ease: "easeInOut" }}
      />

      {/* Hero Content */}
      <div className="max-w-3xl text-center z-10">
        {/* Title */}
        <motion.h1
          className="text-4xl sm:text-5xl font-extrabold tracking-tight leading-tight text-transparent bg-clip-text bg-gradient-to-r from-[#00FF84] to-[rgb(100,181,246)] drop-shadow-lg px-4 sm:px-0"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1 }}
        >
          Biology Vocabulary Mastery with Spaced Repetition
        </motion.h1>

        {/* Description */}
        <motion.p
          className="mt-4 text-base sm:text-lg text-gray-300 leading-relaxed"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.2 }}
        >
          Enhance your <b>biology vocabulary</b> with an <b>intelligent spaced repetition</b>
          system. Instead of simple word lists, this tool dynamically adjusts
          <b> review timing</b> based on your learning patterns. Designed for <b>A/L
          Biology</b> students.
        </motion.p>

        {/* Call to Action Buttons */}
        <motion.div
          className="mt-10 flex flex-wrap justify-center gap-4 sm:gap-6"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          {/* Button that Scrolls to Topic Summary Section */}
          <motion.button
            onClick={scrollToSummarize} // Calls function to scroll smoothly
            className="inline-flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#00FF84] text-[#00FF84] font-semibold rounded-lg hover:bg-[#00FF84] hover:text-black hover:rounded-2xl hover:shadow-lg transition-all duration-300 group"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <RocketLaunchIcon className="w-6 h-6 text-[#00FF84] group-hover:text-black transition-all duration-300" />
            Start Exploring
          </motion.button>
        </motion.div>
      </div>
    </section>
  );
};

export default Hero;
