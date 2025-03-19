import React, { useState } from "react";
import {
  TrophyIcon,
  UsersIcon,
  ShareIcon,
} from "@heroicons/react/24/outline";
import leaderboardImage from "../../assets/image/leaderboard.png"; // Replace with actual image
import { motion } from "framer-motion";
import TopicSummaryModal from "../Summarization/TopicSummaryModal";
import LeaderboardModal from "./LeaderboardModal";

const CompeteAndLearn = () => {
  const [isModalOpen, setIsModalOpen] = useState(false); // Modal state

  return (
    <section className="relative bg-gray-200 px-6 sm:px-12 py-16  min-h-[calc(100vh-96px)] items-center flex">
      {/* Content Wrapper */}
      <div className="relative flex flex-col sm:flex-row items-center justify-between max-w-7xl mx-auto">
        {/* Left Side - Image & Description with Gradient Background */}
        <div className="w-full sm:w-1/2 flex justify-center relative order-2 sm:pl-16">
          <div className="relative bg-[#140342] shadow-lg rounded-lg overflow-hidden w-full max-w-lg">
            {/* Image Section with diagonal cut */}
            <div className="relative flex justify-center w-full p-8 px-16">
              <img
                src={leaderboardImage}
                alt="Leaderboard"
                className="w-72 mx-auto object-cover"
              />
            </div>

            {/* Text Section */}
            <div className="p-6 bg-[#140342] text-white">
              <h3 className="text-lg font-semibold">Compete and Learn</h3>
              <p className="mt-2 text-sm">
                Challenge yourself with the <b>SM-2 spaced repetition algorithm</b>
                and track your progress on the <b>Leaderboard</b>. Earn points,
                rank higher, and <b>share your score</b> with friends!
              </p>
            </div>
          </div>
        </div>

        {/* Right Side - Features & View Leaderboard Button */}
        <div className="w-full sm:w-1/2 flex flex-col justify-center mt-10 sm:mt-0 order-1">
          <h2 className="text-3xl font-bold">Friendly Competetion</h2>

          <div className="mt-6 space-y-4">
            {/* Feature 1 */}
            <div className="flex items-start space-x-3">
              <TrophyIcon className="w-8 h-8 text-yellow-500" />
              <div>
                <p className="font-semibold">Earn Points</p>
                <p className="text-gray-600 text-sm">
                  Answer questions correctly and <b>score points</b> to climb the
                  leaderboard.
                </p>
              </div>
            </div>

            {/* Feature 2 */}
            <div className="flex items-start space-x-3">
              <UsersIcon className="w-8 h-8 text-blue-500" />
              <div>
                <p className="font-semibold">Compete with Friends</p>
                <p className="text-gray-600 text-sm">
                  Compare scores with others and <b>challenge your peers</b> in
                  learning.
                </p>
              </div>
            </div>

            {/* Feature 3 */}
            <div className="flex items-start space-x-3">
              <ShareIcon className="w-8 h-8 text-green-500" />
              <div>
                <p className="font-semibold">Share Your Score</p>
                <p className="text-gray-600 text-sm">
                  Let your friends know about your achievements by <b>sharing
                  your score</b>.
                </p>
              </div>
            </div>
          </div>

          {/* View Leaderboard Button */}
          <motion.div
            className="mt-10 flex justify-center sm:justify-start" // Center on mobile, left-align on larger screens
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
              View Leaderboard
            </motion.button>
          </motion.div>
        </div>
      </div>

      {/* Leaderboard Modal */}
      {isModalOpen && (
        <LeaderboardModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
        />
      )}
    </section>
  );
};

export default CompeteAndLearn;
