import React, { useState } from "react";
import {
  ChartBarIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
} from "@heroicons/react/24/outline";
import progressImage from "../../assets/image/progress.png"; // Replace with actual image
import { motion } from "framer-motion";
import GenerateNotesModal from "../Summarization/GenerateNotesModal";

const ViewProgress = () => {
  const [isModalOpen, setIsModalOpen] = useState(false); // Modal state

  return (
    <section className="relative bg-gray-100 px-6 sm:px-12 py-16">
      {/* Content Wrapper */}
      <div className="relative flex flex-col sm:flex-row items-center justify-between max-w-7xl mx-auto">
        {/* Left Side - Image & Description with Gradient Background */}
        <div className="w-full sm:w-1/2 flex justify-center relative">
          <div className="relative bg-gray-200 shadow-lg rounded-lg overflow-hidden w-full max-w-lg">
            {/* Image Section */}
            <div className="relative">
              <img
                src={progressImage}
                alt="View Progress"
                className="w-96 h-96 object-cover mx-auto"
              />
            </div>

            {/* Text Section */}
            <div className="p-6 bg-[#140342] text-white">
              <h3 className="text-lg font-semibold">Track Your Progress</h3>
              <p className="mt-2 text-sm">
                Monitor your <b>learning journey</b> with real-time stats on
                <b> accuracy</b>, <b>completion rates</b>, and <b>review frequency</b>.
              </p>
            </div>
          </div>
        </div>

        {/* Right Side - Features & View Progress Button */}
        <div className="w-full sm:w-1/2 flex flex-col justify-center sm:pl-16 mt-10 sm:mt-0">
          <h2 className="text-3xl font-bold">Progress with Insights</h2>

          <div className="mt-6 space-y-4">
            {/* Feature 1 */}
            <div className="flex items-start space-x-3">
              <ChartBarIcon className="w-8 h-8 text-green-500" />
              <div>
                <p className="font-semibold">Detailed Insights</p>
                <p className="text-gray-600 text-sm">
                  Get statistics on <b>your accuracy</b> and <b>study habits</b>.
                </p>
              </div>
            </div>

            {/* Feature 2 */}
            <div className="flex items-start space-x-3">
              <CheckCircleIcon className="w-8 h-8 text-blue-500" />
              <div>
                <p className="font-semibold">Mastery Tracking</p>
                <p className="text-gray-600 text-sm">
                  See which words you <b>know well</b> and which need more practice.
                </p>
              </div>
            </div>
          </div>

          {/* View Progress Button */}
          <motion.div
            className="mt-10 flex justify-center sm:justify-start"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <motion.button
              onClick={() => setIsModalOpen(true)} // Opens Modal
              className="inline-flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#140342] text-[#140342]
    font-semibold rounded-lg 
    hover:bg-[#140342] hover:text-white hover:rounded-2xl hover:shadow-lg transition-all duration-300 group"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              View Your Progress
            </motion.button>
          </motion.div>
        </div>
      </div>

      {/* View Progress Modal */}
      {isModalOpen && (
        <GenerateNotesModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
        />
      )}
    </section>
  );
};

export default ViewProgress;
