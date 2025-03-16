import React, { useState, useEffect } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import { Disclosure } from "@headlessui/react";
import { AiOutlineFileText, AiOutlineDown } from "react-icons/ai";
import LoadingScreen from "../LoadingScreen/LoadingScreen";
import { QA_URL } from "../util/config";

const QuestionAndAnsweringStudyMaterials = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [studentId, setStudentId] = useState("")

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        let storedStudentId = localStorage.getItem("user");
        if (storedStudentId) {
          storedStudentId = JSON.parse(storedStudentId).email;
          setStudentId(storedStudentId);
        }
        const response = await axios.post(`${QA_URL}/student-analytics`, {
          student_id: storedStudentId,
        });

        if (response.data.status === "success") {
          setAnalytics(response.data.analytics);
        } else {
          setError("Failed to fetch analytics.");
        }
      } catch (err) {
        setError("Error fetching data. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [studentId]);

  if (loading) {
    return <LoadingScreen />;
  }

  if (error) {
    return <div className="text-center text-red-500 font-semibold">{error}</div>;
  }

  const materials = analytics?.matched_study_materials || [];

  return (
    <div className="p-6 bg-gray-100 min-h-screen w-full max-w-screen-lg mx-auto md:mt-20">
      <h1 className="text-3xl font-bold text-gray-900 mb-6 text-center md:mt-9">📚 Personalized Study Materials</h1>

      {materials.length === 0 ? (
        <div className="text-center text-gray-500 font-semibold">No study materials available.</div>
      ) : (
        <div className="space-y-6">
          {materials.map((material, index) => (
            <motion.div
              key={material["Document ID"] || index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="bg-white shadow-md rounded-xl p-5 border-l-4 border-indigo-500"
            >
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-3">
                  <AiOutlineFileText className="text-indigo-500 text-2xl" />
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900">{material.Topic}</h2>
                    <p className="text-sm text-gray-500">{material["Sub-topic"]}</p>
                  </div>
                </div>
                <span className="bg-indigo-100 text-indigo-600 text-xs px-3 py-1 rounded-full hidden lg:inline">
                  {material.Source}
                </span>
              </div>

              <Disclosure>
                {({ open }) => (
                  <>
                    <Disclosure.Button className="flex w-full justify-between items-center mt-4 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-md">
                      <span className="text-sm font-medium text-gray-700">View Content</span>
                      <AiOutlineDown
                        className={`transition-transform duration-200 ${open ? "rotate-180" : "rotate-0"}`}
                      />
                    </Disclosure.Button>
                    <Disclosure.Panel className="mt-4 text-gray-700 text-sm leading-relaxed p-3 bg-gray-50 rounded-md">
                      {material["Text Content"]}
                    </Disclosure.Panel>
                  </>
                )}
              </Disclosure>
            </motion.div>
          ))}
        </div>
      )}

      {analytics?.recommendations && (
        <div className="mt-8 p-6 bg-white shadow-md rounded-xl">
          <h2 className="text-xl font-bold text-gray-900 mb-4">🔍 Recommendations</h2>
          <div className="text-sm text-gray-700">
            <strong>Learning Path:</strong>
            <ul className="list-disc ml-5 mt-2">
              {analytics.recommendations.learning_path.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default QuestionAndAnsweringStudyMaterials;
