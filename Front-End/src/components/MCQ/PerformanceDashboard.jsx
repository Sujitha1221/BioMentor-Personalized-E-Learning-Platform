import React, { useEffect, useState } from "react";
import api from "../axios/api";
import { Line, Bar } from "react-chartjs-2";
import "chart.js/auto";
import {
  FaTrophy,
  FaChartLine,
  FaUserClock,
  FaLightbulb,
} from "react-icons/fa";
import QuizLoadingScreen from "./loadingPage/QuizLoadingScreen";

const PerformanceDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [performanceGraph, setPerformanceGraph] = useState(null);
  const [progressInsights, setProgressInsights] = useState(null);
  const [comparisonData, setComparisonData] = useState(null);
  const [engagementScore, setEngagementScore] = useState(null);
  const [loading, setLoading] = useState(true); // ✅ Unified loading state

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
          api.get(`/users/dashboard_data/${user.user_id}`, { headers }),
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

        setLoading(false); // ✅ Stop loading after data is fetched
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
    <div className="min-h-screen p-10 mt-0 sm:mt-20 bg-gray-100 text-gray-900">
      <h1 className="text-4xl font-bold text-center text-indigo-700 mb-6">
        📊 User Performance Dashboard
      </h1>
      <p className="text-center text-lg text-gray-700 max-w-3xl mx-auto mb-8">
        Welcome to your personalized **Performance Dashboard**!🎯 Here, you can
        track your quiz history, analyze your **accuracy trends**, compare your
        scores with other users, and gain **AI-driven insights** to improve your
        learning. Keep practicing and watch your performance grow!🚀
      </p>

      {/* Key Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        <div className="bg-white p-6 shadow-lg rounded-lg text-center">
          <FaTrophy className="text-yellow-500 text-4xl mx-auto" />
          <h2 className="text-xl font-semibold mt-4">Total Quizzes</h2>
          <p className="text-2xl font-bold">
            {dashboardData?.total_quizzes || 0}
          </p>
        </div>
        <div className="bg-white p-6 shadow-lg rounded-lg text-center">
          <FaUserClock className="text-blue-500 text-4xl mx-auto" />
          <h2 className="text-xl font-semibold mt-4">Engagement Score</h2>
          <p className="text-2xl font-bold">
            {engagementScore?.engagement_score ?? "N/A"}%
          </p>
        </div>
      </div>

      {/* Performance Trend Chart */}
      <div className="bg-white p-6 shadow-lg rounded-lg mb-10">
        <h2 className="text-2xl font-semibold mb-4">
          📈 Performance Over Time
        </h2>
        {performanceGraph?.quiz_numbers?.length > 0 ? (
          <Line
            data={{
              labels: performanceGraph.quiz_numbers.map((num) => `Quiz ${num}`),
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
          />
        ) : (
          <p className="text-lg text-gray-500">
            No quiz performance data available yet.
          </p>
        )}
      </div>

      {/* AI-Driven Insights */}
      <div className="bg-white p-6 shadow-lg rounded-lg mb-10">
        <h2 className="text-2xl font-semibold mb-4 flex items-center">
          <FaLightbulb className="mr-2 text-yellow-500" /> AI Insights
        </h2>
        <p className="text-lg font-semibold">
          {progressInsights?.suggestion ??
            "No insights available yet. Start taking quizzes!"}
        </p>
      </div>

      {/* Accuracy Comparison */}
      <div className="bg-white p-6 shadow-lg rounded-lg mb-10">
        <h2 className="text-2xl font-semibold mb-4">
          🏆 Comparison with Other Users
        </h2>
        {comparisonData?.user_accuracy !== undefined ? (
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
          />
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
