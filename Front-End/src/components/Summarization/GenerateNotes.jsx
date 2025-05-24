import React, { useState } from "react";
import {
  GlobeAltIcon,
  BookOpenIcon,
  ExclamationTriangleIcon,
} from "@heroicons/react/24/outline";
import notesImage from "../../assets/image/notes.png"; // Replace with actual image
import { motion } from "framer-motion";
import GenerateNotesModal from "./GenerateNotesModal"; // Import the modal

const GenerateNotes = () => {
  const [isModalOpen, setIsModalOpen] = useState(false); // Modal state

  return (
    <section className="relative bg-gray-100 px-6 sm:px-12 py-16">
      {/* Content Wrapper */}
      <div className="relative flex flex-col sm:flex-row items-center justify-between max-w-7xl mx-auto">
        {/* Left Side - Image & Description with Gradient Background */}
        <div className="w-full sm:w-1/2 flex justify-center relative">
          <div className="relative bg-[#140342] shadow-lg rounded-lg overflow-hidden w-full max-w-lg">
            {/* Image Section with diagonal cut */}
            <div className="relative">
              <img
                src={notesImage}
                alt="Generate Notes"
                className="w-full h-80 object-cover"
              />
            </div>

            {/* Text Section */}
            <div className="p-6 bg-[#140342] text-white">
              <h3 className="text-lg font-semibold">
                Generate Notes Instantly
              </h3>
              <p className="mt-2 text-sm">
                Enter any <b>topic or keyword</b> to generate well-structured
                notes using <b>approved resources</b>. Each note is concise,
                covering all the essential <b>key points</b> for better
                understanding.
              </p>
            </div>
          </div>
        </div>

        {/* Right Side - Features & Generate Button */}
        <div className="w-full sm:w-1/2 flex flex-col justify-center sm:pl-16 mt-10 sm:mt-0">
          <h2 className="text-3xl font-bold">How It Works</h2>

          <div className="mt-6 space-y-4">
            {/* Feature 1 */}
            <div className="flex items-start space-x-3">
              <BookOpenIcon className="w-8 h-8 text-green-500" />
              <div>
                <p className="font-semibold">Approved Content</p>
                <p className="text-gray-600 text-sm">
                  Notes are derived from <b>trusted sources</b> to ensure
                  reliability.
                </p>
              </div>
            </div>

            {/* Feature 2 */}
            <div className="flex items-start space-x-3">
              <GlobeAltIcon className="w-8 h-8 text-blue-500" />
              <div>
                <p className="font-semibold">Multi-Language Support</p>
                <p className="text-gray-600 text-sm">
                  Notes can be <b>translated</b> into <b>Sinhala & Tamil</b> for
                  accessibility.
                </p>
              </div>
            </div>

            {/* Feature 3 */}
            <div className="flex items-start space-x-3">
              <ExclamationTriangleIcon className="w-8 h-8 text-red-500" />
              <div>
                <p className="font-semibold">Translation Accuracy</p>
                <p className="text-gray-600 text-sm">
                  <strong className="text-red-600">
                    Translations are only accurate up to a certain extent.
                  </strong>
                </p>
              </div>
            </div>
          </div>

          {/* Generate Notes Button */}
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
              Generate Notes
            </motion.button>
          </motion.div>
        </div>
      </div>

      {/* Generate Notes Modal */}
      {isModalOpen && (
        <GenerateNotesModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
        />
      )}
    </section>
  );
};

export default GenerateNotes;
