import React, { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import {
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

const TopicSummaryModal = ({ isOpen, onClose }) => {
  const [topic, setTopic] = useState("");
  const [wordCount, setWordCount] = useState("");
  const [summary, setSummary] = useState(
    "Your summarized topic text will appear here..."
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
    setTopic("");
    setWordCount("");
    setSummary("Your summarized text will appear here...");
    setIsSummaryGenerated(false);
    setIsLoading(false);
    setTaskId(null);
    setAudioUrl(null);
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

    if (!topic.trim() || !wordCount.trim()) {
      setAlert({
        message: "Please enter a topic and word count.",
        type: "warning",
      });
      setIsLoading(false);
      return;
    }

    try {
      const formData = new FormData();
      formData.append("query", topic);
      formData.append("word_count", wordCount);

      const response = await axios.post(
        `${SUMMARIZE_URL}/process-query/`,
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );

      if (response.data && response.data.summary) {
        setSummary(response.data.summary);
        setIsSummaryGenerated(true);
        setTaskId(response.data.summary_file.split("/").pop());
        // setAlert({
        //   message: "Summary generated successfully!",
        //   type: "success",
        // });
      } else {
        throw new Error("Invalid response from the server.");
      }
    } catch (error) {
      console.error("Error fetching summary:", error);

      if (error.response && error.response.data && error.response.data.detail) {
        setAlert({ message: error.response.data.detail, type: "error" });
      } else {
        setAlert({
          message: "Failed to generate summary. Try again.",
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
        { responseType: "blob" }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "summary.pdf");
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      setAlert({
        message: "Summary downloaded successfully!",
        type: "success",
      });
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
        { responseType: "blob" }
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

  // Safely close modal
  const handleClose = () => {
    if (typeof onClose === "function") {
      console.log("Closing modal...");
      onClose();
    } else {
      console.error("onClose is not a function!");
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

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center p-4 z-50"
      onClick={handleClose} // Clicking outside modal closes it
    >
      {isLoading && <ModalLoadingScreen />}
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

              // Show alert if word count is below 100
              if (parseInt(value) < 100) {
                setAlert({
                  message: "Word count must be at least 100.",
                  type: "warning",
                });
              } else {
                setAlert({ message: "", type: "" }); // Clear alert if valid
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
        !wordCount.trim() || !topic.trim()
          ? "opacity-50 cursor-not-allowed" // Disabled styling
          : ""
      }`}
              disabled={
                !wordCount.trim() || !topic.trim() || parseInt(wordCount) < 100
              }
            >
              Process Summary
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
              className="absolute top-2.5 right-5 bg-gray-200 p-2 rounded-md transition duration-300 hover:bg-gray-400"
              aria-label="Copy Summary"
            >
              {copied ? (
                <FaCheck className="text-green-600" />
              ) : (
                <FaRegCopy className="text-gray-700" />
              )}
            </button>
          </div>

          {/* Download Summary */}
          <div className="flex justify-center mt-3">
            <motion.button
              onClick={handleDownloadSummary}
              className={`flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#00FF84] bg-[#00FF84] text-[#140342] font-semibold rounded-lg 
            transition-transform duration-300 hover:scale-105 hover:bg-[#00cc70] ${
              !isSummaryGenerated ? "opacity-50 cursor-not-allowed" : ""
            }`}
              disabled={!isSummaryGenerated}
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

export default TopicSummaryModal;
