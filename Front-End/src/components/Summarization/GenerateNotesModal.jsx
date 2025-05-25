import React, { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import {
  FaRegCopy,
  FaDownload,
  FaCheck,
  FaPlay,
  FaPause,
  FaVolumeUp,
  FaTimes,
} from "react-icons/fa";
import { MdOutlineClose } from "react-icons/md";
import axios from "axios";
import ModalLoadingScreen from "../LoadingScreen/ModalLoadingScreen";
import AlertMessage from "../Alert/Alert"; // Import Alert Component
import { SUMMARIZE_URL } from "../util/config";

const GenerateNotesModal = ({ isOpen, onClose }) => {
  const [topic, setTopic] = useState("");
  const [language, setLanguage] = useState("english");
  const [notes, setNotes] = useState(
    "Your generated notes will appear here..."
  );
  const [isGenerating, setIsGenerating] = useState(false);
  const [isNotesGenerated, setIsNotesGenerated] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [downloadLink, setDownloadLink] = useState(null);
  const [audioLink, setAudioLink] = useState(null);
  const [copied, setCopied] = useState(false);
  const [alert, setAlert] = useState({ message: "", type: "" });
  const [isMediaPlayerOpen, setIsMediaPlayerOpen] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const audioRef = useRef(null);

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
  const resetOutputStates = () => {
    setNotes("Your generated notes will appear here...");
    setIsGenerating(false);
    setIsNotesGenerated(false);
    setDownloadLink(null);
    setAudioLink(null);
    setAudioUrl(null);
    setIsPlaying(false);
    setCurrentTime(0);
    setDuration(0);
    setVolume(1);
    setPlaybackSpeed(1);
    setIsMediaPlayerOpen(false);
    setAlert({ message: "", type: "" });
    setCopied(false);
  };

  const handleGenerateNotes = async () => {
    if (!topic.trim()) {
      setAlert({ message: "Please enter a topic.", type: "warning" });
      return;
    }

    setIsGenerating(true);
    setIsLoading(true);
    setNotes("Generating notes... Please wait.");
    setDownloadLink(null);
    setAudioLink(null); // Reset audio link

    try {
      const formData = new FormData();
      formData.append("topic", topic);

      let selectedLang = "";
      if (language === "tamil") {
        selectedLang = "ta";
      } else if (language === "sinhala") {
        selectedLang = "si";
      }

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
        console.log("Notes response:", response.data);

        if (response.data.download_link) {
          setDownloadLink(response.data.download_link);
        }

        if (language === "english" && response.data.voice_file) {
          const audioPath = `${SUMMARIZE_URL}${response.data.voice_file}`;
          const audioRes = await axios.get(audioPath, { responseType: "blob" });

          if (audioRes.status === 200 && audioRes.data.size > 0) {
            const blobUrl = URL.createObjectURL(audioRes.data);
            setAudioLink(response.data.voice_file); // keep for download path
            setAudioUrl(blobUrl); // preload for player and quick access
          } else {
            console.warn("Audio file was not loaded correctly.");
          }
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

      const fileExtension = language === "english" ? "pdf" : "txt";
      const blobType =
        fileExtension === "pdf" ? "application/pdf" : "text/plain";

      const url = window.URL.createObjectURL(
        new Blob([response.data], { type: blobType })
      );
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `${topic}_notes.${fileExtension}`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error("Error downloading notes:", error);
      setAlert({
        message: "Failed to download notes. Please try again.",
        type: "error",
      });
    }
  };

  const handleFetchAudio = () => {
    if (!audioUrl) {
      setAlert({
        message: "Audio not ready yet. Try again shortly.",
        type: "warning",
      });
      return;
    }

    setIsMediaPlayerOpen(true);

    setTimeout(() => {
      if (audioRef.current) {
        audioRef.current.src = audioUrl;
        audioRef.current.play();
        setIsPlaying(true);
      }
    }, 200);
  };

  const handleDownloadAudio = () => {
    if (!audioUrl) {
      setAlert({ message: "Audio not ready for download.", type: "warning" });
      return;
    }

    const link = document.createElement("a");
    link.href = audioUrl;
    link.setAttribute("download", `${topic}_notes.mp3`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const togglePlayPause = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleTimeUpdate = () =>
    setCurrentTime(audioRef.current?.currentTime || 0);
  const handleLoadedMetadata = () =>
    setDuration(audioRef.current?.duration || 0);
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
  const handlePlaybackSpeedChange = (e) => {
    const speed = parseFloat(e.target.value);
    audioRef.current.playbackRate = speed;
    setPlaybackSpeed(speed);
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
        className="bg-white rounded-2xl shadow-xl w-[600px] h-auto max-h-screen overflow-y-auto p-6 transition-all max-w-full sm:p-6 relative"
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
          onChange={(e) => {
            setTopic(e.target.value);
            resetOutputStates();
          }}
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
          onChange={(e) => {
            setLanguage(e.target.value);
            resetOutputStates();
          }}
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

        {downloadLink && (
          <div className="flex justify-center mt-3">
            <motion.button
              onClick={handleDownloadNotes}
              className="flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#00FF84] bg-[#00FF84] text-[#140342] font-semibold rounded-lg hover:bg-[#00cc70]"
            >
              <FaDownload /> Download Notes
            </motion.button>
          </div>
        )}
        {language === "english" && audioLink && (
          <div className="mt-4">
            <label className="font-semibold text-[#140342]">
              Audible Notes
            </label>
            <div className="flex gap-4 mt-2">
              <motion.button
                onClick={handleFetchAudio}
                className="flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#140342] text-white bg-[#140342] font-semibold rounded-lg hover:bg-[#32265a]"
              >
                <FaPlay /> Play
              </motion.button>
              <motion.button
                onClick={handleDownloadAudio}
                className="flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#00FF84] bg-[#00FF84] text-[#140342] font-semibold rounded-lg hover:bg-[#00cc70]"
              >
                <FaDownload /> Download Audio
              </motion.button>
            </div>
          </div>
        )}
      </div>
      {isMediaPlayerOpen && audioUrl && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
          <div
            className="bg-white p-6 rounded-lg shadow-lg w-96 relative"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-lg font-bold text-[#140342]">Media Player</h3>
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
  );
};

export default GenerateNotesModal;
