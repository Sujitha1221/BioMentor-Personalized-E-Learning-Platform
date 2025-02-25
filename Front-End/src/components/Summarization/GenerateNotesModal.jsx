import React, { useState,useEffect } from "react";
import { motion } from "framer-motion";
import { FaRegCopy, FaDownload } from "react-icons/fa";
import { MdOutlineClose } from "react-icons/md";

const GenerateNotesModal = ({ isOpen, onClose }) => {
  const [topic, setTopic] = useState("");
  const [language, setLanguage] = useState("english"); // Default to English
  const [notes, setNotes] = useState("Your generated notes will appear here...");
  const [isGenerating, setIsGenerating] = useState(false);
  const [isNotesGenerated, setIsNotesGenerated] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  

    useEffect(() => {
      if (isOpen) {
        resetModal();
        document.body.style.overflow = "hidden";
      } else {
        document.body.style.overflow = "auto";
      }
    }, [isOpen]);

    const resetModal = () => {
        setTopic("");
        setLanguage("");
        setNotes("Your summarized text will appear here...");
        setIsNotesGenerated(false);
        setIsLoading(false);

      };

  const handleGenerateNotes = () => {
    if (!topic.trim()) {
      alert("Please enter a topic.");
      return;
    }

    setIsGenerating(true);
    setTimeout(() => {
      setNotes(`Generated notes for topic: "${topic}" in ${language.toUpperCase()}`);
      setIsGenerating(false);
      setIsNotesGenerated(true);
    }, 2000);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(notes);
    alert("Notes copied!");
  };

  const handleDownloadNotes = () => {
    if (language !== "english") return;

    const blob = new Blob([notes], { type: "text/plain" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `${topic}_notes.txt`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (!isOpen) return null;


  
  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center p-4 z-50"
      onClick={onClose} // Close modal when clicking outside
    >
      <div
        className="bg-white rounded-2xl shadow-xl w-[600px] max-h-[90vh] p-6 transition-all max-w-full sm:p-6 relative"
        onClick={(e) => e.stopPropagation()} // Prevent modal from closing when clicking inside
      >
        {/* Modal Header */}
        <div className="relative mb-4 px-5">
          <h2 className="text-2xl font-bold text-[#140342] text-center w-full">
            Generate Notes
          </h2>
          <button
            aria-label="Close Modal"
            className="absolute right-5 top-0 text-gray-500 hover:text-gray-700 text-xl transition duration-200"
            onClick={onClose}
          >
            <MdOutlineClose />
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="max-h-[70vh] overflow-y-auto px-5 space-y-4">
          {/* Topic Input */}
          <label htmlFor="topic-input" className="block font-semibold text-[#140342]">
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

          {/* Language Selection */}
          <label htmlFor="language-select" className="block font-semibold text-[#140342]">
            Select Language
          </label>
          <select
            id="language-select"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-lg text-gray-700 focus:border-[#140342] focus:ring-[#140342]"
          >
            <option value="english">English</option>
            <option value="tamil">Tamil</option>
            <option value="sinhala">Sinhala</option>
          </select>

          {/* Generate Notes Button */}
          <motion.div className="mt-4 flex justify-center">
            <motion.button
              onClick={handleGenerateNotes}
              className={`inline-flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#140342] text-white bg-[#140342] font-semibold rounded-lg 
              transition-transform duration-300 hover:scale-105 hover:bg-[#32265a] ${
                !topic.trim() ? "opacity-50 cursor-not-allowed" : ""
              }`}
              disabled={!topic.trim()}
            >
              {isGenerating ? "Generating..." : "Generate Notes"}
            </motion.button>
          </motion.div>

          {/* Notes Output */}
          <label className="font-semibold text-[#140342]">Generated Notes</label>
          <div className="relative">
            <textarea
              rows="5"
              value={notes}
              readOnly
              className="w-full p-2 border border-gray-300 rounded-lg text-gray-700 bg-gray-100 focus:border-[#140342] focus:ring-[#140342]"
            ></textarea>
            <button
              onClick={handleCopy}
              className="absolute top-2 right-2 bg-gray-200 p-2 rounded-md transition duration-300 hover:bg-gray-400"
              aria-label="Copy Notes"
            >
              <FaRegCopy />
            </button>
          </div>

          {/* Download Notes (Only for English) */}
          {language === "english" && (
            <div className="flex justify-center mt-3">
              <motion.button
                onClick={handleDownloadNotes}
                className={`flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#00FF84] bg-[#00FF84] text-[#140342] font-semibold rounded-lg 
                transition-transform duration-300 hover:scale-105 hover:bg-[#00cc70] ${
                  !isNotesGenerated ? "opacity-50 cursor-not-allowed" : ""
                }`}
                disabled={!isNotesGenerated}
              >
                <FaDownload /> Download Notes
              </motion.button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default GenerateNotesModal;
