import React from "react";
import { motion } from "framer-motion";
import { DocumentTextIcon, AcademicCapIcon } from "@heroicons/react/24/outline";

const Hero = ({ scrollToEvaluate, scrollToAssignQuestion }) => {
  return (
    <section className="relative h-screen flex flex-col items-center justify-center text-white overflow-hidden bg-[#140342] px-4 sm:px-6">
      {/* Animated Logo */}
      <motion.img
        src="https://plus.unsplash.com/premium_vector-1706709710787-05e3f59294cf?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8bWVkaWNhbHxlbnwwfHwwfHx8MA%3D%3D"
        alt="Evaluation Image"
        className="w-60 h-40 sm:w-72 sm:h-48 mt-4 sm:mt-20 mb-2 sm:mb-6"
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
          AI-Powered Answer Evaluation & Question Assignment
        </motion.h1>

        {/* Description */}
        <motion.p
          className="mt-4 text-base sm:text-lg text-gray-300 leading-relaxed"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.2 }}
        >
          Evaluate student answers with **AI-driven scoring** and **assign new biology questions** instantly.
        </motion.p>

        {/* Call to Action Buttons */}
        <motion.div
          className="mt-10 flex flex-wrap justify-center gap-4 sm:gap-6"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          {/* Button that Scrolls to Answer Evaluation Section */}
          <motion.button
            onClick={scrollToEvaluate}
            className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-slate-300 hover:bg-[#140342] hover:text-[#64B5F6] text-black font-semibold rounded-lg shadow-md transition-all duration-300 group"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <DocumentTextIcon className="w-6 h-6 text-black group-hover:text-[#64B5F6] transition-all duration-300" />
            Evaluate Answer
          </motion.button>

          {/* Button that Scrolls to Question Assignment Section */}
          <motion.button
            onClick={scrollToAssignQuestion}
            className="inline-flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#00FF84] text-[#00FF84] font-semibold rounded-lg hover:bg-[#00FF84] hover:text-black hover:rounded-2xl hover:shadow-lg transition-all duration-300 group"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <AcademicCapIcon className="w-6 h-6 text-[#00FF84] group-hover:text-black group-hover:stroke-black transition-all duration-300" />
            Assign Question
          </motion.button>
        </motion.div>
      </div>
    </section>
  );
};

export default Hero;
