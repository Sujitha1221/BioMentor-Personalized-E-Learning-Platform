import React, { useState } from "react";
import {
  DocumentArrowUpIcon,
  SpeakerWaveIcon,
  ClipboardDocumentListIcon,
  AdjustmentsHorizontalIcon,
  PuzzlePieceIcon,
} from "@heroicons/react/24/outline";
import learningImg from "../../assets/image/vocab-mastery.jpg";
import { motion } from "framer-motion";
import VocabularyMasteryModal from "./VocabularyMasteryModal";

const VocabularyMastery = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <section className="relative bg-gray-100 px-6 sm:px-12 py-16 min-h-[calc(100vh-96px)] items-center flex">
      {/* Content Wrapper */}
      <div className="relative flex flex-col sm:flex-row items-center justify-between max-w-7xl mx-auto">
        {/* Left Side - Image & Description with Gradient Background */}
        <div className="w-full sm:w-1/2 flex justify-center relative">
          <div className="relative bg-[#140342] shadow-lg rounded-lg overflow-hidden w-full max-w-lg">
            <div className="relative">
              <img
                src={learningImg}
                alt="Vocabulary Mastery"
                className="w-full h-72 object-cover"
                style={{
                  clipPath: "polygon(0% 0%, 100% 0%, 100% 85%, 0% 100%)",
                }}
              />
            </div>

            {/* Text Section */}
            <div className="p-6 text-black p-6 bg-[#140342] text-white">
              <h3 className="text-lg font-semibold">
                Master Biology Vocabulary Efficiently
              </h3>
              <p className="mt-2 text-sm">
                Learn and retain essential biology vocabulary using the powerful <b>SM-2 spaced repetition algorithm</b>. Strengthen your recall and track your progress through an engaging <b>Leaderboard system</b>.
              </p>
            </div>
          </div>
        </div>

        {/* Right Side - Features & Info */}
        <div className="w-full sm:w-1/2 flex flex-col justify-center sm:pl-16 mt-10 sm:mt-0">
          <h2 className="text-3xl font-bold">Improve Vocabulary Memory</h2>

          <div className="mt-6 grid grid-cols-2 gap-6">
            {[  
              {
                icon: <SpeakerWaveIcon className="w-8 h-8 text-rose-400" />, 
                label: "Audible Definitions", 
                desc: "Listen to pronunciation and explanations to reinforce learning.",
              },
              {
                icon: <AdjustmentsHorizontalIcon className="w-8 h-8 text-[#FF6347]" />, 
                label: "SM-2 Algorithm", 
                desc: "A scientifically proven method to improve long-term retention.",
              },
              {
                icon: <PuzzlePieceIcon className="w-8 h-8 text-[#140342]" />, 
                label: "Gamified Learning", 
                desc: "Answer questions to measure progress and enhance recall.",
              },
              {
                icon: <DocumentArrowUpIcon className="w-8 h-8 text-green-400" />, 
                label: "Leaderboard", 
                desc: "Compete with peers and track your vocabulary mastery rank.",
              },
            ].map(({ icon, label, desc }) => (
              <div key={label} className="flex items-start space-x-3">
                {icon}
                <div>
                  <p className="font-semibold">{label}</p>
                  <p className="text-gray-600 text-sm">{desc}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Start Learning Button */}
          <motion.div
            className="mt-10 flex flex-wrap gap-4 sm:gap-6"
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
              Start Learning
            </motion.button>
          </motion.div>
        </div>
      </div>

      {/* Learning Modal */}
      <VocabularyMasteryModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </section>
  );
};

export default VocabularyMastery;
