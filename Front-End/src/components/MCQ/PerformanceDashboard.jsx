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
        ] = await Promise.all([
          api.get(`/responses/dashboard_data/${user.user_id}`, { headers }),
          api.get(`/responses/performance_graph/${user.user_id}`, { headers }),
          api.get(`/responses/progress_insights/${user.user_id}`, { headers }),
          api.get(`/responses/user_performance_comparison/${user.user_id}`, {
            headers,
          }),
          api.get(`/responses/engagement_score/${user.user_id}`, { headers }),
        ]);

        setDashboardData(dashboardRes.data);
        setPerformanceGraph(performanceGraphRes.data);
        setProgressInsights(progressRes.data);
        setComparisonData(comparisonRes.data);
        setEngagementScore(engagementRes.data);

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
