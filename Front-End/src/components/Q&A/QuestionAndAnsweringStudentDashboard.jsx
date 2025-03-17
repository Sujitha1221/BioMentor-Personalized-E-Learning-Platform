import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  CartesianGrid,
} from "recharts";
import { motion } from "framer-motion";
import LoadingScreen from "../LoadingScreen/LoadingScreen";
import {
  AiOutlineUser,
  AiOutlineBarChart,
  AiOutlineRise,
  AiOutlineLineChart,
} from "react-icons/ai";
import { QA_URL } from "../util/config";

const QuestionAndAnsweringStudentDashboard = () => {
  const [studentData, setStudentData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [studentId, setStudentId] = useState("");

  useEffect(() => {
    let storedStudentId = localStorage.getItem("user");
    if (storedStudentId) {
      storedStudentId = JSON.parse(storedStudentId).email;
      setStudentId(storedStudentId);
    }
    axios
      .post(`${QA_URL}/student-analytics`, { student_id: storedStudentId })
      .then((response) => {

        // Classify strengths and weaknesses based on final score threshold of 65
        const strengths = [];
        const weaknesses = [];

        response.data.analytics.evaluations.forEach((evaluation) => {
          console.log();
          if (evaluation.evaluation_result.final_score > 65) {
            strengths.push(evaluation.question);
          } else {
            weaknesses.push(evaluation.question);
          }
        });

        response.data.analytics.feedback_report.strengths = strengths;
        response.data.analytics.feedback_report.weaknesses = weaknesses;

        setStudentData(response.data.analytics);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching student analytics:", error);
        setLoading(false);
      });
  }, []);

  if (loading) return <LoadingScreen />;
  if (!studentData)
    return (
      <div className="text-center text-red-500 text-lg font-semibold">
        No Data Found
      </div>
    );

  return (
    <div className="p-6 bg-gray-100 min-h-screen w-full max-w-screen-xl mx-auto md:mt-20">
      {/* Dashboard Header - Floating Title with Badge System */}
      <div className="w-full flex flex-col sm:flex-row justify-between items-center py-6 px-4">
        {/* Title Container */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center sm:text-left"
        >
          {/* Main Title with Floating Effect */}
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 tracking-tight">
            <span className="text-indigo-600">Student</span> Analytics Dashboard
          </h1>

          {/* Subtitle for Engagement */}
          <p className="text-gray-500 text-lg sm:text-xl mt-1">
            Insights & Performance Metrics
          </p>
        </motion.div>

        {/* School Year Badge */}
        <motion.div
          initial={{ opacity: 0, x: 10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
          className="flex items-center gap-3"
        ></motion.div>
      </div>

      {/* KPI Grid Layout - Glassmorphic, 3D, Animated */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6 }}
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mt-8"
      >
        {[
          {
            title: "Student ID",
            value: studentData.student_id,
            icon: <AiOutlineUser />,
          },
          {
            title: "Total Evaluations",
            value: studentData.evaluations.length,
            icon: <AiOutlineBarChart />,
          },
          {
            title: "Proficiency Level",
            value: "Intermediate",
            icon: <AiOutlineRise />,
          },
          {
            title: "Last Evaluation",
            value: new Date(
              studentData.score_trends.timestamps.at(-1)
            ).toLocaleDateString(),
            icon: <AiOutlineLineChart />,
          },
        ].map((item, index) => (
          <motion.div
            key={index}
            whileHover={{ scale: 1.05, rotate: 1 }}
            className="relative p-6 rounded-xl bg-white/50 backdrop-blur-lg shadow-xl border border-gray-300 hover:border-indigo-500 transition-all flex flex-col items-center justify-center text-center"
          >
            <div className="text-indigo-500 text-4xl">{item.icon}</div>
            <h3 className="text-gray-600 text-sm uppercase font-semibold mt-2">
              {item.title}
            </h3>
            <motion.p
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="text-2xl font-bold text-gray-900"
            >
              {item.value}
            </motion.p>
            {/* Gradient Border Effect */}
            <div className="absolute inset-0 border-2 border-transparent rounded-xl transition-all hover:border-indigo-400"></div>
          </motion.div>
        ))}
      </motion.div>

      {/* Performance Breakdown & Score Trends */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
        <div className="bg-white p-6 rounded-xl shadow-md w-full hover:shadow-lg">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">
            📊 Performance Breakdown
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={[
                {
                  metric: "Semantic",
                  score: studentData.average_scores.semantic_score,
                },
                {
                  metric: "TF-IDF",
                  score: studentData.average_scores.tfidf_score,
                },
                {
                  metric: "Jaccard",
                  score: studentData.average_scores.jaccard_score,
                },
                {
                  metric: "Grammar",
                  score: studentData.average_scores.grammar_score,
                },
              ]}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="metric" />
              <YAxis />
              <Tooltip cursor={{ fill: "#e0e7ff" }} />
              <Bar dataKey="score" fill="#6366F1" radius={[5, 5, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-md w-full hover:shadow-lg">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">
            📈 Score Trends Over Time
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart
              data={studentData.score_trends.timestamps.map((date, index) => ({
                date,
                semantic: studentData.score_trends.scores.semantic_score[index],
                tfidf: studentData.score_trends.scores.tfidf_score[index],
                jaccard: studentData.score_trends.scores.jaccard_score[index],
                grammar: studentData.score_trends.scores.grammar_score[index],
              }))}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip cursor={{ strokeDasharray: "3 3" }} />
              <Legend />
              <Line
                type="monotone"
                dataKey="semantic"
                stroke="#2563EB"
                strokeWidth={3}
              />
              <Line
                type="monotone"
                dataKey="tfidf"
                stroke="#10B981"
                strokeWidth={3}
              />
              <Line
                type="monotone"
                dataKey="jaccard"
                stroke="#F59E0B"
                strokeWidth={3}
              />
              <Line
                type="monotone"
                dataKey="grammar"
                stroke="#EF4444"
                strokeWidth={3}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Strengths & Weaknesses - Gamified & Modernized */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="bg-gradient-to-r from-purple-100 to-indigo-100 p-6 rounded-xl shadow-lg w-full mt-8"
      >
        <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center flex items-center justify-center gap-2">
          🚀 Your Performance Analysis
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Strengths Section */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="bg-white bg-opacity-90 backdrop-blur-lg p-6 rounded-2xl shadow-md"
          >
            <h3 className="text-xl font-semibold text-green-700 flex items-center gap-2">
              🎯 Strengths
            </h3>
            <div className="mt-4 space-y-2">
              {studentData.feedback_report.strengths.map((strength, index) => (
                <div key={index} className="flex items-center gap-3">
                  <span className="text-green-600 text-lg">✅</span>
                  <div className="flex-1">
                    <div className="text-gray-700 font-semibold">
                      {strength}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Weaknesses Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="bg-white bg-opacity-90 backdrop-blur-lg p-6 rounded-2xl shadow-md"
          >
            <h3 className="text-xl font-semibold text-red-700 flex items-center gap-2">
              ⚠️ Weaknesses
            </h3>
            <div className="mt-4 space-y-2">
              {studentData.feedback_report.weaknesses.map((weakness, index) => (
                <div key={index} className="flex items-center gap-3">
                  <span className="text-red-600 text-lg">❌</span>
                  <div className="flex-1">
                    <div className="text-gray-700 font-semibold">
                      {weakness}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </motion.div>

      {/* Peer Comparison Graph */}
      <div className="bg-white p-6 rounded-xl shadow-md w-full mt-8">
        <h2 className="text-xl font-semibold text-gray-700 mb-4">
          📊 Peer Comparison
        </h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart
            data={[
              {
                metric: "Semantic",
                student: studentData.average_scores.semantic_score,
                class: studentData.class_average?.semantic_score || 0,
              },
              {
                metric: "TF-IDF",
                student: studentData.average_scores.tfidf_score,
                class: studentData.class_average?.tfidf_score || 0,
              },
              {
                metric: "Jaccard",
                student: studentData.average_scores.jaccard_score,
                class: studentData.class_average?.jaccard_score || 0,
              },
              {
                metric: "Grammar",
                student: studentData.average_scores.grammar_score,
                class: studentData.class_average?.grammar_score || 0,
              },
            ]}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="metric" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="student" fill="#4F46E5" name="Student Score" />
            <Bar dataKey="class" fill="#F59E0B" name="Class Average" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default QuestionAndAnsweringStudentDashboard;
