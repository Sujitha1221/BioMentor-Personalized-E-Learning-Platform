import React, { useState, useEffect } from "react";
import axios from "axios";
import { MdOutlineClose } from "react-icons/md";
import { FaTrophy } from "react-icons/fa";

const API_BASE_URL = "http://127.0.0.1:8000/leaderboard";

const LeaderboardModal = ({ isOpen, onClose }) => {
  const [leaderboard, setLeaderboard] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (isOpen) {
      fetchLeaderboard();
    }
  }, [isOpen]);

  const fetchLeaderboard = async () => {
    try {
      setIsLoading(true);
      const response = await axios.get(`${API_BASE_URL}/top5`);
      if (response.data && response.data.top_5) {
        setLeaderboard(response.data.top_5);
      } else {
        console.error("Invalid response format");
      }
      setIsLoading(false);
    } catch (error) {
      console.error("Error fetching leaderboard:", error);
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl w-[500px] p-6 relative text-center">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 text-gray-500 hover:text-gray-700"
        >
          <MdOutlineClose size={24} />
        </button>

        <h2 className="text-2xl font-bold text-gray-800 mb-4">🏆 Leaderboard</h2>

        {isLoading ? (
          <p className="text-lg font-semibold">Loading leaderboard...</p>
        ) : leaderboard.length > 0 ? (
          <div className="space-y-3">
            {leaderboard.map((user, index) => (
              <div
                key={user._id}
                className={`flex items-center justify-between px-4 py-2 rounded-lg ${
                  index === 0 ? "bg-yellow-300" : "bg-gray-100"
                }`}
              >
                <div className="flex items-center gap-3">
                  <span className="text-lg font-semibold">{index + 1}.</span>
                  <span className="text-lg font-medium">{user.username}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-lg font-semibold">{user.score}</span>
                  {index === 0 && <FaTrophy className="text-yellow-500" />}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-lg font-semibold">No leaderboard data available.</p>
        )}
      </div>
    </div>
  );
};

export default LeaderboardModal;
