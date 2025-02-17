import React from "react";
import { motion } from "framer-motion";
import { DocumentTextIcon, AcademicCapIcon } from "@heroicons/react/24/outline";
import logo from "../../assets/Logo.png"; // Adjust path as needed

const Hero = () => {
  return (
    <section className="relative h-screen flex flex-col items-center justify-center text-white overflow-hidden bg-[#140342] px-4 sm:px-6">
      {/* Animated Logo */}
      <motion.img
  src={logo}
  alt="Bio Mentor Logo"
  className="w-40 h-40 sm:w-48 sm:h-48 mt-4 sm:mt-20 mb-2 sm:mb-6"
  initial={{ opacity: 0, scale: 0.8 }}
  animate={{ opacity: 1, scale: [1, 1.05, 1] }}
  transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
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
Your Biology Digest: Learn More in Less Time
</motion.h1>

{/* Description */}
<motion.p
          className="mt-4 text-base sm:text-lg text-gray-300 leading-relaxed"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.2 }}
        >
Generate clear and concise summaries of <b>biology topics</b> from <b>documents</b>. Instead of simple text extraction, this tool restructures key information for clarity and readability. Designed for <b>A/L Biology students</b>, it extracts concepts from <b>approved educational resources</b> and offers <b>voice output for enhanced learning</b>.        </motion.p>



        {/* CTA Buttons - Styled to Match the Provided Image */}
        <motion.div
          className="mt-10 flex flex-wrap justify-center gap-4 sm:gap-6"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          {/* Solid Button */}
          <motion.a
            href="#document-summary"
            className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-slate-300 hover:bg-[#140342] hover:text-[#6440FB] text-black font-semibold rounded-lg shadow-md transition-all duration-300 group" // Added group class
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }} // Slight bounce effect on click
          >
            <DocumentTextIcon className="w-6 h-6 text-black group-hover:text-[#6440FB] transition-all duration-300" />
            Summarize a Document
          </motion.a>

          {/* Outlined Button */}
          <motion.a
            href="#topic-summary"
            className="inline-flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#00FF84] text-[#00FF84] font-semibold rounded-lg hover:bg-[#00FF84] hover:text-black hover:rounded-2xl hover:shadow-lg transition-all duration-300 group" // Added group class
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }} // Slight bounce effect on click
          >
            <AcademicCapIcon className="w-6 h-6 text-[#00FF84] group-hover:text-black group-hover:stroke-black transition-all duration-300" />
            Summarize by Topic
          </motion.a>
        </motion.div>
      </div>
    </section>
  );
};

export default Hero;
