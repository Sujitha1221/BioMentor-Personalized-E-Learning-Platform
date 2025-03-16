import React from "react";
import { motion } from "framer-motion";
import { AcademicCapIcon } from "@heroicons/react/24/outline";
import mcq from "./mcq.webp";

const Hero = ({ firstSectionRef }) => {
  // Function to scroll smoothly to the first section
  const handleScroll = () => {
    firstSectionRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <section className="relative h-screen flex flex-col items-center justify-center text-white overflow-hidden bg-[#140342] px-4 sm:px-6">
      {/* Animated AI Learning Icon */}
      <motion.img
        src={mcq}
        alt="AI-Powered Learning"
        className="w-64 sm:w-[25rem] h-60 mt-4 sm:mt-20"
        animate={{ x: [0, -3, 3, -3, 3, 0], opacity: [1, 0.9, 1] }}
        transition={{ duration: 1.2, repeat: Infinity, ease: "easeInOut" }}
      />

      {/* Hero Content */}
      <div className="max-w-3xl text-center z-10">
        {/* Title */}
        <motion.h1
          className="text-4xl sm:text-5xl font-extrabold tracking-tight leading-tight text-transparent bg-clip-text bg-gradient-to-r from-[#00FF84] to-[rgb(100,181,246)] drop-shadow-lg px-4 sm:px-0"
          initial={{ opacity: 0, y: -20, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 1 }}
        >
          Quiz. Learn. Repeat. The Smart Way to Study!
        </motion.h1>

        {/* Description */}
        <motion.p
          className="mt-6 text-base sm:text-lg text-gray-200 leading-relaxed"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.2 }}
        >
          Prepare for your A/L Biology exam with dynamically generated quizzes!
          Our intelligent system creates unique questions every time, helping
          you study efficiently, track progress, and master key concepts with
          personalized learning. 🚀🔬
        </motion.p>

        {/* Call to Action Buttons */}
        <motion.div
          className="mt-7 mb-10 flex flex-wrap justify-center gap-4 sm:gap-6"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          {/* Main Button */}
          <motion.button
            onClick={handleScroll}
            className="inline-flex items-center justify-center gap-2 px-8 py-3 border-2 border-[#00FF84] text-[#00FF84] text-lg font-semibold rounded-xl hover:bg-[#00FF84] hover:text-black hover:shadow-[0px_0px_15px_rgba(0,255,132,0.7)] transition-all duration-300 group"
            whileHover={{ scale: 1.07 }}
            whileTap={{ scale: 0.95 }}
          >
            <AcademicCapIcon className="w-6 h-6 text-[#00FF84] group-hover:text-black transition-all duration-300" />
            Start Your Learning Journey
          </motion.button>
        </motion.div>
      </div>
    </section>
  );
};

export default Hero;
