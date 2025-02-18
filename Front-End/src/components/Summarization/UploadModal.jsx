import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { FaFileUpload, FaRegCopy, FaDownload, FaPlay } from "react-icons/fa";
import { MdOutlineClose } from "react-icons/md";

const UploadModal = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState("document");
  const [selectedFile, setSelectedFile] = useState(null);
  const [wordCount, setWordCount] = useState("");
  const [inputText, setInputText] = useState("");
  const [summary, setSummary] = useState(
    "Your summarized text will appear here..."
  );

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "auto";
    }
  }, [isOpen]);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(summary);
    alert("Summary copied!");
  };

  const handleDownload = () => {};

  const handleDownloadAudio = () => {
    alert("Downloading Audible Summary...");
  };

  const handleProcessSummary = () => {
    setSummary("This is the generated summary based on the input.");
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center p-4 z-50">
      <div className="bg-white rounded-2xl shadow-xl w-[800px] max-h-[90vh] p-6 transition-all max-w-full sm:p-6 relative overflow-x-hidden">
        {/* Modal Header */}
        <div className="relative mb-4">
          <h2 className="text-2xl font-bold text-[#140342] text-center w-full">
            Generate Summary
          </h2>
          <button
            aria-label="Close Modal"
            className="absolute right-0 top-0 text-gray-500 hover:text-gray-700 text-xl"
            onClick={onClose}
          >
            <MdOutlineClose />
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="max-h-[70vh] overflow-y-auto overflow-x-hidden">
          {/* Tabs */}
          <div className="flex mb-4 border-b">
            <button
              className={`px-4 py-2 w-1/2 text-lg font-semibold focus:outline-none ${
                activeTab === "document"
                  ? "text-[#140342] border-b-2 border-[#140342]"
                  : "text-gray-500"
              }`}
              onClick={() => setActiveTab("document")}
            >
              Document Summary
            </button>
            <button
              className={`px-4 py-2 w-1/2 text-lg font-semibold focus:outline-none ${
                activeTab === "text"
                  ? "text-[#140342] border-b-2 border-[#140342]"
                  : "text-gray-500"
              }`}
              onClick={() => setActiveTab("text")}
            >
              Text Summary
            </button>
          </div>

          {/* Modal Content */}
          <div className="space-y-4">
            {/* Document-Based Summary */}
            {activeTab === "document" && (
              <>
                <label
                  htmlFor="file-upload"
                  className="block font-semibold text-[#140342]"
                >
                  Upload Document
                </label>
                <div className="border-2 border-dashed border-gray-300 p-6 text-center rounded-lg cursor-pointer hover:border-gray-500 transition-all">
                  <input
                    type="file"
                    accept=".pdf,.doc,.docx,.ppt,.pptx,.txt"
                    onChange={handleFileChange}
                    className="hidden"
                    id="file-upload"
                  />
                  <label htmlFor="file-upload" className="block cursor-pointer">
                    <FaFileUpload className="text-[#140342] text-4xl mx-auto mb-2" />
                    <p className="text-[#140342] font-semibold text-lg">
                      Click to Upload a File
                    </p>
                    <p className="text-sm text-gray-500">
                      Supported formats: PDF, Word, PPT, TXT
                    </p>
                  </label>
                </div>
                {selectedFile && (
                  <p className="text-center text-gray-700 font-medium">
                    {selectedFile.name}
                  </p>
                )}
              </>
            )}

            {/* Text-Based Summary */}
            {activeTab === "text" && (
              <>
                <label
                  htmlFor="text-input"
                  className="block font-semibold text-[#140342]"
                >
                  Enter Text
                </label>
                <textarea
                  id="text-input"
                  rows="5"
                  placeholder="Enter your text to summarize..."
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-lg text-gray-700 focus:border-[#140342] focus:ring-[#140342]"
                ></textarea>
              </>
            )}

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
                className="inline-flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#140342] text-[#140342] font-semibold rounded-lg 
                hover:bg-[#140342] hover:text-white hover:rounded-2xl hover:shadow-lg transition-all duration-300 group"
              >
                Process Summary
              </motion.button>
            </motion.div>

            {/* Summary Output */}
            <div className="relative">
              <label className="font-semibold text-[#140342]">
                Summary Output
              </label>
              <textarea
                rows="5"
                value={summary}
                readOnly
                className="w-full p-2 border border-gray-300 rounded-lg text-gray-700 bg-gray-100 focus:border-[#140342] focus:ring-[#140342]"
              ></textarea>
              <button
                onClick={handleCopy}
                className="absolute top-8 right-2 bg-gray-200 p-2 rounded-md hover:bg-gray-300 transition"
                aria-label="Copy Summary"
              >
                <FaRegCopy />
              </button>
            </div>

            {/* Download Summary */}
            <div className="flex justify-center mt-3">
              <motion.button
                onClick={handleDownload}
                className="inline-flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#00FF84] text-[#00FF84] font-semibold rounded-lg 
                hover:bg-[#00FF84] hover:text-[#140342] hover:rounded-2xl hover:shadow-lg transition-all duration-300 group"
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
                  className="flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#6440FB] text-[#6440FB] font-semibold rounded-lg 
                  hover:bg-[#6440FB] hover:text-white hover:shadow-lg transition-all duration-300 group"
                >
                  <FaPlay /> Play
                </motion.button>

                <motion.button
                  onClick={handleDownloadAudio}
                  className="flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#00FF84] text-[#00FF84] font-semibold rounded-lg 
                  hover:bg-[#00FF84] hover:text-[#140342] hover:shadow-lg transition-all duration-300 group"
                >
                  <FaDownload /> Download Audio
                </motion.button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadModal;
