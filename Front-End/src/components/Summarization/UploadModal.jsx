import React, { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import {
  FaFileUpload,
  FaRegCopy,
  FaDownload,
  FaPlay,
  FaPause,
  FaVolumeUp,
  FaTimes,
  FaCheck,
} from "react-icons/fa";
import { MdOutlineClose } from "react-icons/md";
import axios from "axios";
import AlertMessage from "../Alert/Alert";
import ModalLoadingScreen from "../LoadingScreen/ModalLoadingScreen";
import { SUMMARIZE_URL } from "../util/config";
import { jsPDF } from "jspdf";

const UploadModal = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState("document");
  const [selectedFile, setSelectedFile] = useState(null);
  const [wordCount, setWordCount] = useState("");
  const [inputText, setInputText] = useState("");
  const [summary, setSummary] = useState(
    "Your summarized text will appear here..."
  );
  const [isLoading, setIsLoading] = useState(false);
  const [isSummaryGenerated, setIsSummaryGenerated] = useState(false);
  const [taskId, setTaskId] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMediaPlayerOpen, setIsMediaPlayerOpen] = useState(false);
  const [alert, setAlert] = useState({ message: "", type: "" });
  const [copied, setCopied] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [concepts, setConcepts] = useState([]);
  const [isConceptLoading, setIsConceptLoading] = useState(false);
  const [videoSuggestions, setVideoSuggestions] = useState([]);
  const [viewMode, setViewMode] = useState(null); // 'concepts' or 'videos'

  const audioRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      resetModal();
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "auto";
    }
  }, [isOpen]);

  const resetModal = () => {
    setSelectedFile(null);
    setWordCount("");
    setInputText("");
    setSummary("Your summarized text will appear here...");
    setIsSummaryGenerated(false);
    setIsLoading(false);
    setTaskId(null);
    setAudioUrl(null);
    setIsPlaying(false);
    setCurrentTime(0);
    setDuration(0);
    setVolume(1);
    setIsMediaPlayerOpen(false);
    setConcepts([]);
    setVideoSuggestions([]);
    setCopied(false);
    setAlert({ message: "", type: "" });
  };

  const resetOutputStates = () => {
    setSummary("Your summarized text will appear here...");
    setIsSummaryGenerated(false);
    setTaskId(null);
    setAudioUrl(null);
    setIsPlaying(false);
    setCurrentTime(0);
    setDuration(0);
    setVolume(1);
    setIsMediaPlayerOpen(false);
    setConcepts([]);
    setVideoSuggestions([]);
    setCopied(false);
    setAlert({ message: "", type: "" });
  };

  const handleFileChange = (event) => {
    resetOutputStates();
    setSelectedFile(event.target.files[0]);
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

  const handleCopy = () => {
    if (summary) {
      navigator.clipboard.writeText(summary);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleProcessSummary = async () => {
    setIsLoading(true);
    setIsSummaryGenerated(false);
    setSummary("Processing...");
    setConcepts([]);
    setVideoSuggestions([]);
    setViewMode(null);

    if (!wordCount.trim() || parseInt(wordCount) < 100) {
      setAlert({
        message: "Please enter a valid word count (min: 100).",
        type: "error",
      });
      setIsLoading(false);
      return;
    }

    const formData = new FormData();
    formData.append("word_count", wordCount);

    if (activeTab === "document") {
      if (!selectedFile) {
        setAlert({
          message: "Please upload a file to summarize.",
          type: "error",
        });
        setIsLoading(false);
        return;
      }
      formData.append("file", selectedFile);
    } else {
      if (!inputText.trim()) {
        setAlert({ message: "Please enter text to summarize.", type: "error" });
        setIsLoading(false);
        return;
      }
      formData.append("text", inputText);
    }

    try {
      const endpoint =
        activeTab === "document"
          ? `${SUMMARIZE_URL}/process-document/`
          : `${SUMMARIZE_URL}/summarize-text/`;

      const response = await axios.post(endpoint, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      if (response.data && response.data.summary) {
        setSummary(response.data.summary);
        setIsSummaryGenerated(true);
        setTaskId(response.data.summary_file.split("/").pop()); // Extract task_id from API response
      } else {
        throw new Error("Invalid response format");
      }
    } catch (error) {
      console.error("Error processing summary:", error);

      // Check if the error response exists from the backend
      if (error.response && error.response.data && error.response.data.detail) {
        setAlert({
          message: error.response.data.detail, // Display backend error message
          type: "error",
        });
        resetModal();
      } else {
        setAlert({
          message: "Failed to generate summary. Please try again.",
          type: "error",
        });
        resetModal();
      }

      setSummary("Failed to generate summary.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownloadSummary = async () => {
    if (!taskId) {
      setAlert({ message: "Generate a summary first!", type: "error" });
      return;
    }

    try {
      const response = await axios.get(
        `${SUMMARIZE_URL}/download-summary-text/${taskId}`,
        {
          responseType: "blob",
        }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "summary.pdf");
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      // setAlert({
      //   message: "Summary downloaded successfully!",
      //   type: "success",
      // });
    } catch (error) {
      console.error("Error downloading summary:", error);
      setAlert({ message: "Failed to download summary.", type: "error" });
    }
  };

  const handleDownloadAudio = async () => {
    if (!taskId) {
      setAlert({ message: "Generate a summary first!", type: "error" });
      return;
    }

    try {
      const response = await axios.get(
        `${SUMMARIZE_URL}/download-summary-audio/${taskId}`,
        {
          responseType: "blob",
        }
      );

      if (response.status !== 200) {
        throw new Error(`Server returned status ${response.status}`);
      }

      const url = window.URL.createObjectURL(
        new Blob([response.data], { type: "audio/mpeg" })
      );
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "summary.mp3");
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      setAlert({
        message: "Summary Audio downloaded successfully!",
        type: "success",
      });
    } catch (error) {
      console.error("Error downloading audio:", error);
      setAlert({ message: "Failed to download audio.", type: "error" });
    }
  };

  const handleFetchAudio = async () => {
    if (!taskId) {
      setAlert({ message: "Generate a summary first!", type: "error" });
      return;
    }

    try {
      const response = await axios.get(
        `${SUMMARIZE_URL}/download-summary-audio/${taskId}`,
        {
          responseType: "blob",
        }
      );

      if (response.status !== 200) {
        throw new Error(`Server returned status ${response.status}`);
      }

      const audioBlob = new Blob([response.data], { type: "audio/mpeg" });

      if (audioBlob.size === 0) {
        throw new Error("Received empty audio file. Please check the backend.");
      }

      const audioURL = URL.createObjectURL(audioBlob);
      setAudioUrl(audioURL);
      setIsMediaPlayerOpen(true);

      setTimeout(() => {
        if (audioRef.current) {
          audioRef.current.src = audioURL;
          audioRef.current.play();
          setIsPlaying(true);
          setAlert({ message: "Playing audio summary!", type: "success" });
        }
      }, 300);
    } catch (error) {
      console.error("Error fetching audio:", error);
      setAlert({
        message: "Failed to fetch summary audio. Please try again.",
        type: "error",
      });
    }
  };
  const togglePlayPause = () => {
    if (!audioUrl) return;

    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleTimeUpdate = () => {
    setCurrentTime(audioRef.current.currentTime);
  };

  const handleLoadedMetadata = () => {
    setDuration(audioRef.current.duration);
  };

  const handleSeek = (e) => {
    const time = parseFloat(e.target.value);
    audioRef.current.currentTime = time;
    setCurrentTime(time);
  };

  const handleVolumeChange = (e) => {
    const vol = parseFloat(e.target.value);
    audioRef.current.volume = vol;
    setVolume(vol);
  };

  const handlePlaybackSpeedChange = (event) => {
    const speed = parseFloat(event.target.value);
    audioRef.current.playbackRate = speed;
    setPlaybackSpeed(speed);
  };

  const handleFetchConcepts = async () => {
    if (!summary || summary === "Your summarized text will appear here...") {
      setAlert({ message: "Generate a summary first!", type: "error" });
      return;
    }

    setIsConceptLoading(true);
    try {
      const response = await axios.post(`${SUMMARIZE_URL}/concept-breakdown`, {
        text: summary,
      });

      if (response.data?.concepts?.length > 0) {
        setConcepts(response.data.concepts);
        setViewMode("concepts");
        setAlert({
          message: "Concepts extracted successfully!",
          type: "success",
        });
      } else {
        setConcepts([]);
        setAlert({ message: "No concepts found.", type: "warning" });
      }
    } catch (error) {
      console.error("Error fetching concepts:", error);
      setAlert({ message: "Failed to extract concepts.", type: "error" });
    } finally {
      setIsConceptLoading(false);
    }
  };

  const handleFetchConceptVideos = async () => {
    if (!summary || summary === "Your summarized text will appear here...") {
      setAlert({ message: "Generate a summary first!", type: "error" });
      return;
    }

    setIsConceptLoading(true);
    try {
      const response = await axios.post(`${SUMMARIZE_URL}/concept-videos`, {
        mode: "summary",
        text: summary,
      });

      if (response.data?.videos?.length > 0) {
        setVideoSuggestions(response.data.videos);
        setViewMode("videos");
        setAlert({ message: "Videos loaded successfully!", type: "success" });
      } else {
        setVideoSuggestions([]);
        setAlert({ message: "No videos found.", type: "warning" });
      }
    } catch (error) {
      console.error("Error fetching concept videos:", error);
      setAlert({ message: "Failed to load video suggestions.", type: "error" });
    } finally {
      setIsConceptLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center p-4 z-50"
      onClick={handleClose} // Clicking outside modal closes it
    >
      {alert.message && (
        <AlertMessage
          message={alert.message}
          type={alert.type}
          onClose={() => setAlert({ message: "", type: "" })}
        />
      )}
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
            onClick={onClose}
          >
            <MdOutlineClose />
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="max-h-[70vh] overflow-y-auto px-5">
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
                    required
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
                {/* Show selected file name with an option to remove */}
                {selectedFile && (
                  <div className="mt-3 flex justify-center items-center space-x-4">
                    <p className="text-center text-gray-700 font-medium">
                      {selectedFile.name}
                    </p>
                    <button
                      onClick={() => setSelectedFile(null)}
                      className="text-red-500 text-sm font-semibold hover:text-red-700 transition"
                    >
                      Remove
                    </button>
                  </div>
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
                  onChange={(e) => {
                    setInputText(e.target.value);
                    setActiveTab("text");
                    resetOutputStates(); // your custom function for clearing summary/audio/videos/etc.
                  }}
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
              placeholder="Enter word count (min: 100)"
              value={wordCount}
              required
              min="100"
              onChange={(e) => {
                const value = e.target.value;
                setWordCount(value);
                resetOutputStates();

                if (parseInt(value) < 100) {
                  setAlert({
                    message: "Word count must be at least 100.",
                    type: "warning",
                  });
                } else {
                  setAlert({ message: "", type: "" });
                }
              }}
              className={`w-full p-2 border ${
                parseInt(wordCount) < 100 ? "border-red-500" : "border-gray-300"
              } rounded-lg text-gray-700 focus:border-[#140342] focus:ring-[#140342]`}
            />

            {/* Process Button */}
            <motion.div className="mt-4 flex justify-center">
              <motion.button
                onClick={handleProcessSummary}
                className={`inline-flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#140342] text-white bg-[#140342] font-semibold rounded-lg 
      transition-transform duration-300 hover:scale-105 hover:bg-[#32265a] ${
        !wordCount.trim() ||
        parseInt(wordCount) < 100 ||
        (activeTab === "document" && !selectedFile) ||
        (activeTab === "text" && !inputText.trim())
          ? "opacity-50 cursor-not-allowed"
          : ""
      }`}
                disabled={
                  !wordCount.trim() ||
                  parseInt(wordCount) < 100 ||
                  (activeTab === "document" && !selectedFile) ||
                  (activeTab === "text" && !inputText.trim())
                }
              >
                Process Summary
              </motion.button>
            </motion.div>

            {/* Summary Output with Copy Button */}
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
                className="absolute top-8 right-5 bg-gray-200 p-2 rounded-md transition duration-300 hover:bg-gray-400"
                aria-label="Copy Summary"
              >
                {copied ? (
                  <FaCheck className="text-green-600" />
                ) : (
                  <FaRegCopy className="text-gray-700" />
                )}
              </button>
            </div>

            {/* Full-page spinner for both summary or concepts */}
            {(isLoading || isConceptLoading) && <ModalLoadingScreen />}

            {/* Action Buttons */}
            <div className="flex flex-wrap justify-center gap-4 mt-3">
              <motion.button
                onClick={handleDownloadSummary}
                className={`flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#00FF84] bg-[#00FF84] text-[#140342] font-semibold rounded-lg 
    transition-transform duration-300 hover:scale-105 hover:bg-[#00cc70] ${
      !isSummaryGenerated ? "opacity-50 cursor-not-allowed" : ""
    }`}
                disabled={!isSummaryGenerated}
              >
                <FaDownload /> Summary
              </motion.button>

              <motion.button
                onClick={handleFetchConcepts}
                className={`flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#140342] text-white bg-[#140342] font-semibold rounded-lg 
    transition-transform duration-300 hover:scale-105 hover:bg-[#32265a] ${
      !isSummaryGenerated ? "opacity-50 cursor-not-allowed" : ""
    }`}
                disabled={!isSummaryGenerated || isConceptLoading}
              >
                🧠 Keywords
              </motion.button>

              <motion.button
                onClick={handleFetchConceptVideos}
                className={`flex items-center justify-center gap-2 px-6 py-3 border-2 border-gray-600 text-gray-800 bg-gray-200 font-semibold rounded-lg 
    transition-transform duration-300 hover:scale-105 hover:bg-gray-300 ${
      !isSummaryGenerated ? "opacity-50 cursor-not-allowed" : ""
    }`}
                disabled={!isSummaryGenerated || isConceptLoading}
              >
                🎥 Videos
              </motion.button>
            </div>

            {(viewMode === "concepts" || viewMode === "videos") && (
              <div className="mt-6 border-t pt-4 relative">
                <div className="flex justify-between items-center mb-2">
                  <h3 className="text-lg font-semibold text-[#140342]">
                    {viewMode === "concepts"
                      ? "🔍 Extracted Concepts:"
                      : "🎥 Learn More: Concept Videos"}
                  </h3>
                  {viewMode === "concepts" && (
                    <button
                      onClick={() => {
                        const doc = new jsPDF();
                        doc.setFontSize(12);
                        let y = 10;
                        concepts.forEach(({ term, definition }, index) => {
                          doc.setFont("helvetica", "bold");
                          doc.text(`${index + 1}. ${term}`, 10, y);
                          y += 6;
                          doc.setFont("helvetica", "normal");
                          const lines = doc.splitTextToSize(definition, 180);
                          lines.forEach((line) => {
                            if (y > 280) {
                              doc.addPage();
                              y = 10;
                            }
                            doc.text(line, 10, y);
                            y += 6;
                          });
                          y += 4;
                        });
                        doc.save("concepts.pdf");
                      }}
                      className="flex items-center gap-2 text-sm px-4 py-2 bg-gray-200 p-2 rounded-md transition duration-300 hover:bg-gray-400"
                    >
                      <FaDownload />
                    </button>
                  )}
                </div>

                {viewMode === "concepts" ? (
                  <ul className="space-y-2 max-h-60 overflow-y-auto pr-2">
                    {concepts.map((item, index) => {
                      const wikiUrl = `https://en.wikipedia.org/wiki/${item.term.replace(
                        / /g,
                        "_"
                      )}`;
                      return (
                        <li
                          key={index}
                          className="bg-gray-50 p-3 rounded-lg shadow"
                        >
                          <div>
                            <a
                              href={wikiUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-sm font-bold text-blue-800 hover:underline"
                            >
                              🔗 {item.term}
                            </a>
                            <p className="text-sm text-gray-700 mt-1">
                              {item.definition}
                            </p>
                          </div>
                        </li>
                      );
                    })}
                  </ul>
                ) : (
                  <ul className="space-y-3 max-h-60 overflow-y-auto pr-2">
                    {videoSuggestions.map((vid, idx) => (
                      <li
                        key={idx}
                        className="bg-gray-50 p-3 rounded-lg shadow flex gap-4"
                      >
                        <img
                          src={vid.thumbnail}
                          alt={vid.title}
                          className="w-24 h-16 object-cover rounded"
                        />
                        <div>
                          <a
                            href={vid.link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm font-bold text-blue-700 hover:underline"
                          >
                            {vid.title}
                          </a>
                          <p className="text-xs text-gray-500">
                            Channel: {vid.channel}
                          </p>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}

            {/* Audible Summary */}
            <div className="mt-4">
              <label className="font-semibold text-[#140342]">
                Audible Summary
              </label>
              <div className="flex gap-4 mt-2">
                <motion.button
                  onClick={handleFetchAudio}
                  className={`flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#140342] text-white bg-[#140342] font-semibold rounded-lg 
  transition-transform duration-300 hover:scale-105 hover:bg-[#32265a] ${
    !isSummaryGenerated ? "opacity-50 cursor-not-allowed" : ""
  }`}
                  disabled={!isSummaryGenerated}
                >
                  <FaPlay /> Play
                </motion.button>

                <motion.button
                  onClick={handleDownloadAudio}
                  className={`flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#00FF84] bg-[#00FF84] text-[#140342] font-semibold rounded-lg 
  transition-transform duration-300 hover:scale-105 hover:bg-[#00cc70] ${
    !isSummaryGenerated ? "opacity-50 cursor-not-allowed" : ""
  }`}
                  disabled={!isSummaryGenerated}
                >
                  <FaDownload /> Download Audio
                </motion.button>
              </div>
            </div>
          </div>
        </div>
        {isMediaPlayerOpen && audioUrl && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
            <div className="bg-white p-6 rounded-lg shadow-lg w-96 relative">
              <div className="flex justify-between items-center mb-3">
                <h3 className="text-lg font-bold text-[#140342]">
                  Media Player
                </h3>
                <button
                  onClick={() => setIsMediaPlayerOpen(false)}
                  className="text-gray-500 hover:text-gray-700 transition"
                >
                  <FaTimes size={20} />
                </button>
              </div>

              <audio
                ref={audioRef}
                onTimeUpdate={handleTimeUpdate}
                onLoadedMetadata={handleLoadedMetadata}
              />

              <div className="flex justify-center items-center gap-3 mt-3">
                <button
                  onClick={togglePlayPause}
                  className="p-2 rounded-full bg-[#140342] text-white hover:bg-[#32265a] transition"
                >
                  {isPlaying ? <FaPause size={20} /> : <FaPlay size={20} />}
                </button>
                <input
                  type="range"
                  min="0"
                  max={duration}
                  value={currentTime}
                  onChange={handleSeek}
                  className="w-full accent-gray-800"
                />
                <FaVolumeUp />
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={volume}
                  onChange={handleVolumeChange}
                  className="w-20 accent-gray-800"
                />
              </div>

              {/* Playback Speed Control (Focus on Slower and Faster Speeds) */}
              <div className="mt-4 flex justify-center items-center gap-3">
                <label className="text-sm font-semibold text-[#140342]">
                  Speed:
                </label>
                <select
                  value={playbackSpeed}
                  onChange={handlePlaybackSpeedChange}
                  className="border border-gray-300 rounded-md p-1 text-[#140342]"
                >
                  <option value="0.25">0.25x (Very Slow)</option>
                  <option value="0.5">0.5x (Slow)</option>
                  <option value="0.75">0.75x (Moderate)</option>
                  <option value="1">1x (Normal)</option>
                  <option value="1.5">1.5x (Fast)</option>
                  <option value="2">2x (Very Fast)</option>
                </select>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default UploadModal;
