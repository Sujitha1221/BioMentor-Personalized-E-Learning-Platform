import React, { useEffect, useState } from "react";
import axios from "axios";
import { Bar, Pie } from "react-chartjs-2";
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  ArcElement,
} from "chart.js";
import { useNavigate } from "react-router-dom";

ChartJS.register(
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  ArcElement
);

const API_URL = "http://127.0.0.1:8000/flashcards/user/67d6a31ad20c865759215988/stats";

const UserStatsPage = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await axios.get(API_URL);
        setStats(res.data);
        setLoading(false);
      } catch (err) {
        console.error("Failed to load stats", err);
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen text-xl font-semibold text-blue-700">
        Loading stats...
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="flex items-center justify-center min-h-screen text-lg text-red-600">
        Failed to load stats.
      </div>
    );
  }

  const barData = {
    labels: Object.keys(stats.score_distribution),
    datasets: [
      {
        label: "Review Score Count",
        data: Object.values(stats.score_distribution),
        backgroundColor: "#3b82f6",
        borderRadius: 5,
      },
    ],
  };

  const pieData = {
    labels: Object.keys(stats.review_schedule),
    datasets: [
      {
        label: "Upcoming Reviews",
        data: Object.values(stats.review_schedule),
        backgroundColor: [
          "#10b981",
          "#ef4444",
          "#3b82f6",
          "#f59e0b",
          "#8b5cf6",
          "#f97316",
        ],
      },
    ],
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-white p-6">
      <div className="max-w-5xl mx-auto bg-white shadow-2xl rounded-xl p-8">
        <button onClick={() => {navigate("/vocabulary-memorization")}} className="py-2 px-3 rounded bg-red-600 hover:bg-red-700 duration-200 text-white">Back</button>
        <h1 className="text-3xl font-extrabold text-center text-blue-800 mb-6">
          📊 Vocabulary Mastery Stats
        </h1>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-blue-100 p-4 rounded-lg shadow text-center">
            <h2 className="text-lg font-semibold text-blue-800">Username</h2>
            <p className="text-xl font-bold text-blue-600 mt-1">{stats.username}</p>
          </div>
          <div className="bg-green-100 p-4 rounded-lg shadow text-center">
            <h2 className="text-lg font-semibold text-green-800">Total Score</h2>
            <p className="text-xl font-bold text-green-600 mt-1">{stats.total_score}</p>
          </div>
          <div className="bg-yellow-100 p-4 rounded-lg shadow text-center">
            <h2 className="text-lg font-semibold text-yellow-800">Total Reviews</h2>
            <p className="text-xl font-bold text-yellow-600 mt-1">{stats.total_reviews}</p>
          </div>
          <div className="bg-purple-100 p-4 rounded-lg shadow text-center">
            <h2 className="text-lg font-semibold text-purple-800">Avg. Score</h2>
            <p className="text-xl font-bold text-purple-600 mt-1">{stats.average_score}</p>
          </div>
        </div>

        <div className="w-full gap-10">
          <div className="bg-white w-full rounded-lg shadow-lg p-6 border border-gray-100 hover:shadow-xl transition">
            <h3 className="text-xl font-bold text-gray-800 mb-4 text-center">
              📈 Score Distribution
            </h3>
            <Bar data={barData} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserStatsPage;