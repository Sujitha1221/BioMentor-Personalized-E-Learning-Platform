import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { FaRegCopy, FaDownload, FaCheck } from "react-icons/fa";
import { MdOutlineClose } from "react-icons/md";
import axios from "axios";
import ModalLoadingScreen from "../LoadingScreen/ModalLoadingScreen";
import AlertMessage from "../Alert/Alert"; // Import Alert Component
import { SUMMARIZE_URL } from "../util/config";

const GenerateNotesModal = ({ isOpen, onClose }) => {
  const [topic, setTopic] = useState("");
  const [language, setLanguage] = useState("english"); // Default language
  const [notes, setNotes] = useState(
    "Your generated notes will appear here..."
  );
  const [isGenerating, setIsGenerating] = useState(false);
  const [isNotesGenerated, setIsNotesGenerated] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [downloadLink, setDownloadLink] = useState(null);
  const [alert, setAlert] = useState({ message: "", type: "" }); // Alert state
  const [copied, setCopied] = useState(false);

  // Prevent background scrolling when modal is open
  useEffect(() => {
    if (isOpen) {
      resetModal();
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "auto";
    }

    return () => {
      document.body.style.overflow = "auto";
    };
  }, [isOpen]);

  const resetModal = () => {
    setTopic("");
    setLanguage("english");
    setNotes("Your generated notes will appear here...");
    setIsLoading(false);
  };

  const handleGenerateNotes = async () => {
    if (!topic.trim()) {
      setAlert({ message: "Please enter a topic.", type: "warning" });
      return;
    }
  
    setIsGenerating(true);
    setIsLoading(true);
    setNotes("Generating notes... Please wait.");
    setDownloadLink(null); // Reset download link before request
  
    try {
      // Prepare FormData
      const formData = new FormData();
      formData.append("topic", topic);
  
      // Convert language to API expected format
      let selectedLang = "";
      if (language === "tamil") {
        selectedLang = "ta";
      } else if (language === "sinhala") {
        selectedLang = "si";
      }
  
      // Append language if not English
      if (selectedLang) {
        formData.append("lang", selectedLang);
      }
  
      const response = await axios.post(
        `${SUMMARIZE_URL}/generate-notes/`,
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );
  
      if (response.data) {
        setNotes(response.data.structured_notes);
        setIsNotesGenerated(true);
        console.log(response.data)
  
        // Set download link ONLY if API provides it
        if (response.data.download_link) {
          setDownloadLink(response.data.download_link);
        } else {
          setDownloadLink(null);
        }
  
        setAlert({ message: "Notes generated successfully!", type: "success" });
      } else {
        throw new Error("Failed to generate notes. Please try again.");
      }
    } catch (error) {
      console.error("Error generating notes:", error);
      setAlert({
        message: error.response?.data?.detail || "An error occurred.",
        type: "error",
      });
      resetModal();
      setNotes("An unexpected error occurred.");
    } finally {
      setIsGenerating(false);
      setIsLoading(false);
    }
  };  

  const handleCopy = () => {
    if (notes) {
      navigator.clipboard.writeText(notes);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDownloadNotes = async () => {
    if (!downloadLink) return;

    try {
      const response = await axios.get(`${SUMMARIZE_URL}${downloadLink}`, {
        responseType: "blob",
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `${topic}_notes.pdf`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // setAlert({
      //   message: "Notes PDF downloaded successfully!",
      //   type: "success",
      // });
    } catch (error) {
      console.error("Error downloading PDF:", error);
      setAlert({
        message: "Failed to download PDF. Please try again.",
        type: "error",
      });
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center p-4 z-50"
      onClick={onClose}
    >
      {/* Show Loading Screen */}
      {isLoading && <ModalLoadingScreen />}

      {/* Show Alerts */}
      {alert.message && (
        <AlertMessage
          message={alert.message}
          type={alert.type}
          onClose={() => setAlert({ message: "", type: "" })}
        />
      )}

      <div
        className="bg-white rounded-2xl shadow-xl w-[600px] max-h-[90vh] p-6 transition-all max-w-full sm:p-6 relative"
        onClick={(e) => e.stopPropagation()}
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

        {/* Topic Input */}
        <label
          htmlFor="topic-input"
          className="block font-semibold text-[#140342]"
        >
          Enter Topic / Keyword
        </label>
        <input
          id="topic-input"
          type="text"
          placeholder="Enter a topic or keyword (e.g., Photosynthesis)"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          className="w-full p-2 border border-gray-300 rounded-lg text-gray-700 focus:border-[#140342] focus:ring-[#140342]"
        />

        {/* Language Selection */}
        <label
          htmlFor="language-select"
          className="block font-semibold text-[#140342] mt-4"
        >
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
            disabled={!topic.trim() || isGenerating}
          >
            {isGenerating ? "Generating..." : "Generate Notes"}
          </motion.button>
        </motion.div>

        {/* Notes Output */}
        <label className="font-semibold text-[#140342] mt-4 block">
          Generated Notes
        </label>
        <div className="relative">
          <textarea
            rows="5"
            value={notes}
            readOnly
            className="w-full p-2 pr-12 border border-gray-300 rounded-lg text-gray-700 bg-gray-100 focus:border-[#140342] focus:ring-[#140342]"
          />
          <button
            onClick={handleCopy}
            className="absolute top-2.5 right-5 bg-gray-200 p-2 rounded-md transition duration-300 hover:bg-gray-400"
            aria-label="Copy Notes"
          >
            {copied ? (
              <FaCheck className="text-green-600 w-5 h-5" />
            ) : (
              <FaRegCopy className="text-gray-700 w-5 h-5" />
            )}
          </button>
        </div>

        {/* Download Button (Only for English) */}
        {language === "english" && downloadLink && (
          <div className="flex justify-center mt-3">
            <motion.button
              onClick={handleDownloadNotes}
              className="flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#00FF84] bg-[#00FF84] text-[#140342] font-semibold rounded-lg 
                transition-transform duration-300 hover:scale-105 hover:bg-[#00cc70]"
            >
              <FaDownload /> Download Notes
            </motion.button>
          </div>
        )}
      </div>
    </div>
  );
};

export default GenerateNotesModal;
