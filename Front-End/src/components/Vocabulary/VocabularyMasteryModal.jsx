import React, { useState, useEffect } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import { FaArrowRight, FaVolumeUp } from "react-icons/fa";
import { MdOutlineClose } from "react-icons/md";
import SharingModal from "./SharingModal";

const API_BASE_URL = "http://127.0.0.1:8000/flashcards";

const VocabularyMasteryModal = ({ isOpen, onClose }) => {
  const [questions, setQuestions] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [userAnswer, setUserAnswer] = useState("");
  const [flipped, setFlipped] = useState(false);
  const [score, setScore] = useState(0);
  const [timeLeft, setTimeLeft] = useState(20);
  const [isLoading, setIsLoading] = useState(true);
  const username = "Gokul Abisheak";
  const [showSharingModal, setShowSharingModal] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchQuestions();
    }
  }, [isOpen]);

  useEffect(() => {
    if (timeLeft > 0 && isOpen) {
      const timer = setInterval(
        () => setTimeLeft((prev) => Math.max(prev - 1, 0)),
        1000
      );
      return () => clearInterval(timer);
    }
  }, [timeLeft, isOpen]);

  const fetchQuestions = async () => {
    try {
      setIsLoading(true);
      const response = await axios.get(`${API_BASE_URL}/daily/67d6a31ad20c865759215988`);
      if (response.data && response.data.questions) {
        setQuestions(response.data.questions);
        setCurrentIndex(0);
        setScore(0);
        setFlipped(false);
        setTimeLeft(20);
      } else {
        console.error("Invalid response format");
      }
      setIsLoading(false);
    } catch (error) {
      console.error("Error fetching questions:", error);
      setIsLoading(false);
    }
  };

  const handleSpeak = () => {
    if (questions[currentIndex]?.question) {
      speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(questions[currentIndex].question);
      utterance.lang = "en-US";
      utterance.rate = 1;
      utterance.volume = 1;

      const voices = speechSynthesis.getVoices();
      utterance.voice = voices.find((voice) => voice.lang === "en-US") || voices[0];

      speechSynthesis.speak(utterance);
    }
  };

  useEffect(() => {
    const loadVoices = () => {
      speechSynthesis.getVoices();
    };
    loadVoices();
    if (speechSynthesis.onvoiceschanged !== undefined) {
      speechSynthesis.onvoiceschanged = loadVoices;
    }
  }, []);

  const handleAnswerSubmit = async () => {
    if (!userAnswer.trim()) return;

    const questionId = questions[currentIndex]?._id;
    if (!questionId) return;

    try {
      const response = await axios.post(
        `${API_BASE_URL}/answer/67d6a31ad20c865759215988/${questionId}`,
        { user_answer: userAnswer },
        { headers: { "Content-Type": "application/json" } }
      );
      const reviewScore = response.data.review_score || 0;
      setScore((prevScore) => prevScore + reviewScore);
    } catch (error) {
      console.error("Error submitting answer:", error.response?.data || error.message);
    }

    setFlipped(true);
    setTimeLeft(0);
  };

  const handleNextQuestion = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setUserAnswer("");
      setFlipped(false);
      setTimeLeft(20);
    } else {
      submitFinalScore();
    }
  };

  const submitFinalScore = async () => {
    try {
      await axios.post(
        `${API_BASE_URL}/add_score`,
        { username, score },
        { headers: { "Content-Type": "application/json" } }
      );
      setShowSharingModal(true)
    } catch (error) {
      console.error("Error submitting final score:", error.response?.data || error.message);
    }
  };

  if (!isOpen) return null;

  return (
    <>
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl w-[600px] p-6 relative text-center">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 text-gray-500 hover:text-gray-700"
        >
          <MdOutlineClose size={24} />
        </button>

        {isLoading ? (
          <p className="text-lg font-semibold">Loading questions...</p>
        ) : questions.length > 0 ? (
          <div>
            <h2 className="text-xl font-bold mb-4">Vocabulary Mastery</h2>
            <p className="text-lg font-semibold text-blue-600">Score: {score}</p>
            <div className="w-full bg-gray-200 rounded-full h-2.5 mb-2 overflow-hidden">
              <motion.div
                className="bg-blue-600 h-2.5 rounded-full"
                animate={{ width: `${(timeLeft / 20) * 100}%` }}
                transition={{ duration: 1, ease: "linear" }}
              ></motion.div>
            </div>
            <p className="text-sm font-medium text-gray-700">
              Question {currentIndex + 1} / {questions.length}
            </p>
            <motion.div
              className="relative bg-gray-100 p-6 rounded-lg text-lg font-semibold shadow-md cursor-pointer mt-2 flex items-center justify-center"
              animate={{ rotateY: flipped ? 180 : 0 }}
              transition={{ duration: 0.5 }}
              style={{ perspective: "1000px", width: "100%", height: "150px" }}
            >
              <div
                className="absolute w-full h-full flex items-center justify-center text-center"
                style={{ visibility: flipped ? "hidden" : "visible" }}
              >
                <p className="text-xl">{questions[currentIndex]?.answer || "Loading..."}</p>
              </div>
              <div
                className="absolute w-full h-full flex items-center justify-center text-center"
                style={{
                  visibility: flipped ? "visible" : "hidden",
                  transform: "scaleX(-1)",
                }}
              >
                <p className="text-green-600 text-xl">{questions[currentIndex]?.question || "Loading..."}</p>
              </div>
            </motion.div>
            {!flipped ? (
              <div className="mt-4">
                <input
                  type="text"
                  value={userAnswer}
                  onChange={(e) => setUserAnswer(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-lg"
                  placeholder="Enter the term..."
                />
                <button
                  onClick={handleAnswerSubmit}
                  className="mt-3 px-4 py-2 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 w-full"
                >
                  Submit
                </button>
              </div>
            ) : (
              <div className="mt-4 flex gap-2">
                <button
                  onClick={handleNextQuestion}
                  className="px-4 py-2 bg-green-600 text-white font-bold rounded-lg hover:bg-green-700 flex items-center gap-2"
                >
                  <FaArrowRight /> Next
                </button>
                <button
                  onClick={handleSpeak}
                  className="px-4 py-2 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 flex items-center gap-2"
                >
                  <FaVolumeUp /> Pronounce
                </button>
              </div>
            )}
          </div>
        ) : (
          <p className="text-lg font-semibold">No questions available.</p>
        )}
      </div>
    </div>
    <SharingModal isOpen={showSharingModal} onClose={() => {setShowSharingModal(false); onClose()}} score={score} />
    </>
  );
};

export default VocabularyMasteryModal;
