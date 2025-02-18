import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { FaRegCopy, FaDownload, FaPlay } from "react-icons/fa";
import { MdOutlineClose } from "react-icons/md";

const TopicSummaryModal = ({ isOpen, onClose }) => {
  const [topic, setTopic] = useState("");
  const [wordCount, setWordCount] = useState("");
  const [summary, setSummary] = useState(
    "Your summarized topic text will appear here..."
  );

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "auto";
    }
  }, [isOpen]);

  const handleCopy = () => {
    navigator.clipboard.writeText(summary);
    alert("Summary copied!");
  };

  const handleDownload = () => {
    const element = document.createElement("a");
    const file = new Blob([summary], { type: "text/plain" });
    element.href = URL.createObjectURL(file);
    element.download = "topic_summary.txt";
    document.body.appendChild(element);
    element.click();
  };

  const handleProcessSummary = () => {
    setSummary(
      `Summary of topic: ${topic} with ${wordCount} words. This is the generated summary...`
    );
  };

  const handleDownloadAudio = () => {
    alert("Downloading Audible Summary...");
  };

  // Safely close modal
  const handleClose = () => {
    if (typeof onClose === "function") {
      console.log("Closing modal...");
      onClose();
    } else {
      console.error("onClose is not a function!");
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center p-4 z-50"
      onClick={handleClose} // Clicking outside modal closes it
    >
      <div
        className="bg-white rounded-2xl shadow-xl w-[800px] max-h-[90vh] p-6 transition-all max-w-full sm:p-6 relative"
        onClick={(e) => e.stopPropagation()} // Prevent closing when clicking inside modal
      >
        {/* Modal Header */}
        <div className="relative mb-4 px-5">
          <h2 className="text-2xl font-bold text-[#140342] text-center w-full">
            Generate Summary
          </h2>
          <button
            aria-label="Close Modal"
            className="absolute right-5 top-0 text-gray-500 hover:text-gray-700 text-xl transition duration-200"
            onClick={handleClose}
          >
            <MdOutlineClose />
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="max-h-[70vh] overflow-y-auto px-5 space-y-4">
          {/* Topic Input */}
          <label
            htmlFor="topic-input"
            className="block font-semibold text-[#140342]"
          >
            Enter Topic
          </label>
          <input
            id="topic-input"
            type="text"
            placeholder="Enter a topic (e.g., Photosynthesis)"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-lg text-gray-700 focus:border-[#140342] focus:ring-[#140342]"
          />

          {/* Word Count */}
          <label
            htmlFor="word-count"
            className="block font-semibold text-[#140342]"
          >
            Approximate Word Count
          </label>
          <input
            id="word-count"
            type="number"
            placeholder="Enter word count"
            value={wordCount}
            onChange={(e) => setWordCount(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-lg text-gray-700 focus:border-[#140342] focus:ring-[#140342]"
          />

          {/* Process Button */}
          <motion.div className="mt-4 flex justify-center">
            <motion.button
              onClick={handleProcessSummary}
              className="inline-flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#140342] text-white bg-[#140342] font-semibold rounded-lg 
              transition-transform duration-300 hover:scale-105 hover:bg-[#32265a]"
            >
              Generate Summary
            </motion.button>
          </motion.div>

          {/* Summary Output */}
          <label className="font-semibold text-[#140342]">Summary Output</label>
          <div className="relative">
            <textarea
              rows="5"
              value={summary}
              readOnly
              className="w-full p-2 border border-gray-300 rounded-lg text-gray-700 bg-gray-100 focus:border-[#140342] focus:ring-[#140342]"
            ></textarea>
            <button
              onClick={handleCopy}
              className="absolute top-8 right-2 bg-gray-200 p-2 rounded-md transition duration-300 hover:bg-gray-400"
              aria-label="Copy Summary"
            >
              <FaRegCopy />
            </button>
          </div>

          {/* Download Summary */}
          <div className="flex justify-center mt-3">
            <motion.button
              onClick={handleDownload}
              className="inline-flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#00FF84] text-[#140342] bg-[#00FF84] font-semibold rounded-lg 
              transition-transform duration-300 hover:scale-105 hover:bg-[#00cc70]"
            >
              <FaDownload /> Download Summary
            </motion.button>
          </div>

          {/* Audible Summary */}
          <div className="mt-4">
            <label className="font-semibold text-[#140342]">
              Audible Summary
            </label>
            <div className="flex gap-4 mt-2">
              <motion.button
                className="flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#140342] text-white bg-[#140342] font-semibold rounded-lg 
                transition-transform duration-300 hover:scale-105 hover:bg-[#32265a]"
              >
                <FaPlay /> Play
              </motion.button>

              <motion.button
                onClick={handleDownloadAudio}
                className="flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#00FF84] bg-[#00FF84] text-[#140342] font-semibold rounded-lg 
                transition-transform duration-300 hover:scale-105 hover:bg-[#00cc70]"
              >
                <FaDownload /> Download Audio
              </motion.button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TopicSummaryModal;
