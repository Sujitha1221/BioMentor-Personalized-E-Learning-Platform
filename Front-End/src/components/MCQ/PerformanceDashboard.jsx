import React, { useEffect, useState } from "react";
import api from "../axios/api";
import { Line, Bar } from "react-chartjs-2";
import "chart.js/auto";
import {
  FaTrophy,
  FaChartLine,
  FaUserClock,
  FaLightbulb,
  FaStar,
  FaBolt,
  FaMedal,
} from "react-icons/fa";
import QuizLoadingScreen from "./loadingPage/QuizLoadingScreen";
import { motion } from "framer-motion";

const PerformanceDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [performanceGraph, setPerformanceGraph] = useState(null);
  const [progressInsights, setProgressInsights] = useState(null);
  const [comparisonData, setComparisonData] = useState(null);
  const [engagementScore, setEngagementScore] = useState(null);
  const [loading, setLoading] = useState(true);
  const [leaderboard, setLeaderboard] = useState([]);

  const user = JSON.parse(localStorage.getItem("user"));
  const token = localStorage.getItem("token");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const headers = { Authorization: `Bearer ${token}` };

        const [
          dashboardRes,
          performanceGraphRes,
          progressRes,
          comparisonRes,
          engagementRes,
          leaderboardRes,
        ] = await Promise.all([
          api.get(`/responses/dashboard_data/${user.user_id}`, { headers }),
          api.get(`/responses/performance_graph/${user.user_id}`, { headers }),
          api.get(`/responses/progress_insights/${user.user_id}`, { headers }),
          api.get(`/responses/user_performance_comparison/${user.user_id}`, {
            headers,
          }),
          api.get(`/responses/engagement_score/${user.user_id}`, { headers }),
          api.get(`/responses/leaderboard`, { headers }),
        ]);

        setDashboardData({
          ...dashboardRes.data,
          leaderboard: leaderboardRes.data.leaderboard,
        });
        setPerformanceGraph(performanceGraphRes.data);
        setProgressInsights(progressRes.data);
        setComparisonData(comparisonRes.data);
        setEngagementScore(engagementRes.data);
        setLeaderboard(leaderboardRes.data.leaderboard);

        setLoading(false);
      } catch (error) {
        console.error("Error fetching performance data:", error);
        setLoading(false);
      }
    };

    if (user?.user_id && token) {
      fetchData();
    }
  }, [user?.user_id, token]);

  if (loading) {
    return <QuizLoadingScreen />;
  }

  return (
    <div className="min-h-screen p-10 mt-0 sm:mt-20 bg-gradient-to-br from-blue-50 to-indigo-100 text-gray-900">
      <motion.h1
        className="text-5xl font-bold text-center text-indigo-700 mb-6"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        📊 User Performance Dashboard
      </motion.h1>
      <p className="text-center text-lg text-gray-700 max-w-3xl mx-auto mb-8">
        Track your progress, analyze your performance trends, and compare scores
        with peers. Unlock insights to improve your skills and become a quiz
        master! 🚀
      </p>

      {/* 🎖 Dynamic Badge */}
      <div className="flex justify-center mb-10">
        <div className="bg-gradient-to-r from-indigo-100 to-purple-200 p-6 rounded-xl shadow-xl text-center w-full">
          {(() => {
            const totalQuizzes = dashboardData?.total_quizzes || 0;
            const consistency = dashboardData?.consistency_score || 0;
            const lastAccuracy = performanceGraph?.scores?.slice(-1)[0] || 0;

            if (totalQuizzes >= 20 && lastAccuracy >= 90) {
              return (
                <>
                  <h3 className="text-2xl font-bold text-indigo-800">
                    🏆 Ultimate Quiz Champion
                  </h3>
                  <p className="text-gray-700">
                    20+ quizzes completed and stellar accuracy!
                  </p>
                </>
              );
            } else if (consistency >= 80) {
              return (
                <>
                  <h3 className="text-2xl font-bold text-green-700">
                    🔥 Consistency Champion
                  </h3>
                  <p className="text-gray-700">
                    You're taking quizzes like clockwork!
                  </p>
                </>
              );
            } else if (lastAccuracy >= 90) {
              return (
                <>
                  <h3 className="text-2xl font-bold text-purple-700">
                    🎯 Accuracy Ace
                  </h3>
                  <p className="text-gray-700">
                    Recent scores show top-notch precision!
                  </p>
                </>
              );
            } else if (totalQuizzes >= 10) {
              return (
                <>
                  <h3 className="text-2xl font-bold text-yellow-600">
                    💪 Quiz Warrior
                  </h3>
                  <p className="text-gray-700">10+ quizzes down. Keep going!</p>
                </>
              );
            } else {
              return (
                <>
                  <h3 className="text-2xl font-bold text-blue-600">
                    🚀 Rising Star
                  </h3>
                  <p className="text-gray-700">You’re off to a great start!</p>
                </>
              );
            }
          })()}
        </div>
      </div>

      {/* Key Metrics Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        {[
          {
            icon: <FaTrophy className="text-yellow-500 text-4xl mx-auto" />,
            title: "Total Quizzes",
            value: dashboardData?.total_quizzes || 0,
          },
          {
            icon: <FaUserClock className="text-blue-500 text-4xl mx-auto" />,
            title: "Engagement Score",
            value: `${engagementScore?.engagement_score ?? "N/A"}%`,
          },
          {
            icon: <FaMedal className="text-green-500 text-4xl mx-auto" />,
            title: "Consistency Score",
            value: dashboardData?.consistency_score || "N/A",
          },
        ].map((metric, index) => (
          <motion.div
            key={index}
            className="bg-white p-6 shadow-lg rounded-lg text-center hover:shadow-2xl transition-all"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.2 }}
          >
            {metric.icon}
            <h2 className="text-xl font-semibold mt-4">{metric.title}</h2>
            <p className="text-2xl font-bold">{metric.value}</p>
          </motion.div>
        ))}
      </div>

      {/* AI-Driven Insights */}
      <div className="bg-yellow-100 p-6 shadow-lg rounded-lg mb-10 text-center">
        <h2 className="text-2xl font-semibold flex items-center justify-center">
          <FaLightbulb className="mr-2 text-yellow-500" /> AI Insights
        </h2>
        <p className="text-lg font-semibold">
          {progressInsights?.suggestion ??
            "No insights available yet. Start taking quizzes!"}
        </p>
      </div>
      <div className="bg-white p-6 shadow-lg rounded-lg mb-10">
        <h2 className="text-2xl font-semibold mb-6 text-center text-indigo-800">
          🏅 Leaderboard
        </h2>

        {dashboardData?.leaderboard?.length > 0 ? (
          <ul className="space-y-4">
            {dashboardData.leaderboard.map((userItem, index) => {
              const rankEmoji = ["🥇", "🥈", "🥉"][index] || `#${index + 1}`;
              const isCurrentUser = userItem.user_id === user.user_id; // Check if this is the logged-in user
              const userName = userItem.name
                ? `${userItem.name}${isCurrentUser ? " (You)" : ""}`
                : `User ${userItem.user_id.slice(-4)}${
                    isCurrentUser ? " (You)" : ""
                  }`;
              const accuracy = userItem.accuracy;

              return (
                <li
                  key={index}
                  className={`flex items-center justify-between px-4 py-3 rounded-lg shadow-sm ${
                    index === 0
                      ? "bg-yellow-50"
                      : index === 1
                      ? "bg-gray-100"
                      : index === 2
                      ? "bg-orange-100"
                      : "bg-gray-50"
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">{rankEmoji}</span>
                    <span className="text-gray-800 font-medium">
                      {userName}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-indigo-700">
                      {accuracy}%
                    </span>
                    <div className="w-32 bg-gray-200 h-2 rounded-full overflow-hidden">
                      <div
                        className="bg-indigo-500 h-2 rounded-full"
                        style={{ width: `${accuracy}%` }}
                      ></div>
                    </div>
                  </div>
                </li>
              );
            })}
          </ul>
        ) : (
          <p className="text-gray-500 text-center">
            Not enough data for leaderboard.
          </p>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        {/* Performance Trend Chart */}
        <div className="bg-white p-6 shadow-lg rounded-lg mb-10">
          <h2 className="text-2xl font-semibold mb-4">
            📈 Performance Over Time
          </h2>
          {performanceGraph?.quiz_numbers?.length > 0 ? (
            <div className="w-full h-64">
              <Line
                data={{
                  labels: performanceGraph.quiz_numbers.map(
                    (num) => `Quiz ${num}`
                  ),
                  datasets: [
                    {
                      label: "Accuracy (%)",
                      data: performanceGraph.scores,
                      borderColor: "#4F46E5",
                      borderWidth: 2,
                      fill: false,
                    },
                  ],
                }}
                options={{ maintainAspectRatio: false }}
              />
            </div>
          ) : (
            <p className="text-lg text-gray-500">
              No quiz performance data available yet.
            </p>
          )}
        </div>

        {/* Accuracy Comparison Chart */}
        <div className="bg-white p-6 shadow-lg rounded-lg mb-10">
          <h2 className="text-2xl font-semibold mb-4">
            🏆 Comparison with Other Users
          </h2>
          {comparisonData?.user_accuracy !== undefined ? (
            <div className="w-full h-64">
              <Bar
                data={{
                  labels: ["Your Accuracy", "Average Accuracy"],
                  datasets: [
                    {
                      label: "Accuracy (%)",
                      data: [
                        comparisonData?.user_accuracy,
                        comparisonData?.average_accuracy,
                      ],
                      backgroundColor: ["#34D399", "#60A5FA"],
                    },
                  ],
                }}
                options={{ maintainAspectRatio: false }}
              />
            </div>
          ) : (
            <p className="text-lg text-gray-500">
              Not enough data for comparison.
            </p>
          )}
        </div>
        {/* Time Spent Per Difficulty Chart */}
        <div className="bg-white p-6 shadow-lg rounded-lg mb-10">
          <h2 className="text-2xl font-semibold mb-4">
            ⏱ Time Spent by Difficulty
          </h2>
          {dashboardData?.time_easy !== undefined ? (
            <div className="w-full h-64">
              <Bar
                data={{
                  labels: ["Easy", "Medium", "Hard"],
                  datasets: [
                    {
                      label: "Total Time (s)",
                      data: [
                        dashboardData.time_easy,
                        dashboardData.time_medium,
                        dashboardData.time_hard,
                      ],
                      backgroundColor: ["#A7F3D0", "#93C5FD", "#FCA5A5"],
                    },
                  ],
                }}
                options={{
                  maintainAspectRatio: false,
                  scales: {
                    y: {
                      beginAtZero: true,
                    },
                  },
                }}
              />
            </div>
          ) : (
            <p className="text-lg text-gray-500">
              Not enough data for time tracking.
            </p>
          )}
        </div>
      </div>
      {/* Strongest & Weakest Areas */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-green-100 p-6 shadow-lg rounded-lg text-center">
          <h2 className="text-xl font-semibold">💪 Strongest Area</h2>
          <p className="text-2xl font-bold">
            {dashboardData?.strongest_area ?? "N/A"}
          </p>
        </div>
        <div className="bg-red-100 p-6 shadow-lg rounded-lg text-center">
          <h2 className="text-xl font-semibold">⚠️ Weakest Area</h2>
          <p className="text-2xl font-bold">
            {dashboardData?.weakest_area ?? "N/A"}
          </p>
        </div>
      </div>
    </div>
  );
};

export default PerformanceDashboard;
