import React, { useState } from "react";
import {
  DocumentArrowUpIcon,
  SpeakerWaveIcon,
  ClipboardDocumentListIcon,
  AdjustmentsHorizontalIcon,
} from "@heroicons/react/24/outline";
import uploadImg from "../../assets/image/doc-summarize.jpeg";
import { motion } from "framer-motion";
import UploadModal from "./UploadModal"; // Import the modal component

const SummarizeDocument = () => {
  const [isModalOpen, setIsModalOpen] = useState(false); // State for modal

  return (
    <section className="relative bg-gray-100 px-6 sm:px-12 py-16">
      {/* Content Wrapper */}
      <div className="relative flex flex-col sm:flex-row items-center justify-between max-w-7xl mx-auto">
        {/* Left Side - Image & Description with Gradient Background */}
        <div className="w-full sm:w-1/2 flex justify-center relative">
          <div className="relative bg-[#140342] shadow-lg rounded-lg overflow-hidden w-full max-w-lg">
            {/* Image with diagonal cut effect */}
            <div className="relative">
              <img
                src={uploadImg}
                alt="Upload Document"
                className="w-full h-72 object-cover"
                style={{
                  clipPath: "polygon(0% 0%, 100% 0%, 100% 85%, 0% 100%)",
                }}
              />
            </div>

            {/* Text Section */}
            <div className="p-6 text-black p-6 bg-[#140342] text-white">
              <h3 className="text-lg font-semibold">
                Summarize Documents with Ease
              </h3>
              <p className="mt-2 text-sm">
                Upload PDFs, Word docs, PPTs, text files, or paste text directly
                to generate <b>structured summaries</b> instantly. The tool
                ensures <b>no key details are lost</b> and offers an{" "}
                <b>audible summary</b> for hands-free learning.
              </p>
            </div>
          </div>
        </div>

        {/* Right Side - Upload Info & Features */}
        <div className="w-full sm:w-1/2 flex flex-col justify-center sm:pl-16 mt-10 sm:mt-0">
          <h2 className="text-3xl font-bold">How It Works</h2>

          <div className="mt-6 grid grid-cols-2 gap-6">
            {[
              {
                icon: (
                  <DocumentArrowUpIcon className="w-8 h-8 text-green-400" />
                ),
                label: "PDF Files",
                desc: "Upload your study notes in PDF format.",
              },
              {
                icon: (
                  <DocumentArrowUpIcon className="w-8 h-8 text-[#6440FB]" />
                ),
                label: "Word Docs",
                desc: "Summarize resource materials.",
              },
              {
                icon: (
                  <DocumentArrowUpIcon className="w-8 h-8 text-[#FFAA00]" />
                ),
                label: "PowerPoint",
                desc: "Extract key points from presentations.",
              },
              {
                icon: (
                  <ClipboardDocumentListIcon className="w-8 h-8 text-[#140342]" />
                ),
                label: "Paste Text",
                desc: "Manually enter text for summarization.",
              },
              {
                icon: <SpeakerWaveIcon className="w-8 h-8 text-rose-400" />,
                label: "Audible Summary",
                desc: "Listen to summaries for hands-free learning.",
              },
              {
                icon: (
                  <AdjustmentsHorizontalIcon className="w-8 h-8 text-[#FF6347]" />
                ),
                label: "Customizable Word Count",
                desc: "Adjust the number of words in your summary as needed.",
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

          {/* Upload Button */}
          <motion.div
            className="mt-10 flex flex-wrap justify-center gap-4 sm:gap-6"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <motion.button
              onClick={() => setIsModalOpen(true)} // Opens Modal on Click
              className="inline-flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#140342] text-[#140342]
              font-semibold rounded-lg 
              hover:bg-[#140342] hover:text-white hover:rounded-2xl hover:shadow-lg transition-all duration-300 group"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Upload or Paste Text
            </motion.button>
          </motion.div>
        </div>
      </div>

      {/* Upload Modal */}
      <UploadModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </section>
  );
};

export default SummarizeDocument;
