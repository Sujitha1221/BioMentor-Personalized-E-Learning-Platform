import React, { useEffect, useState } from "react";
import MindMap from "./MindMap";
import axios from "axios";
import { QA_URL } from "../util/config";
import LoadingScreen from "../LoadingScreen/LoadingScreen";
import { useNavigate } from "react-router-dom";

const MindMapPage = () => {
  const [mindMapData, setMindMapData] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchMindMap = async () => {
      let storedStudentId = localStorage.getItem("user");
      if (storedStudentId) {
        storedStudentId = JSON.parse(storedStudentId).email;
      }

      if (!storedStudentId) return;

      setLoading(true);
      try {
        const res = await axios.post(`${QA_URL}/student-mind-map`, {
          student_id: storedStudentId,
        });
        setMindMapData(res.data.mind_map || null);
      } catch (err) {
        console.error("Error fetching mind map:", err);
        setMindMapData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchMindMap();
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 px-4 py-6 md:px-8 lg:px-12 mt-20">
      <div className="max-w-7xl w-full mx-auto bg-white rounded-xl shadow-md p-4 sm:p-6 md:p-8">
        <div className="flex flex-col sm:flex-row justify-between items-center mb-6 gap-4">
          <h2 className="text-xl sm:text-2xl font-bold text-gray-800 text-center sm:text-left">
            🧠 Mind Map of Weak Areas
          </h2>
          <button
            onClick={() => navigate(-1)}
            className="inline-flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#140342] text-[#140342]
    font-semibold rounded-lg hover:bg-[#140342] hover:text-white hover:rounded-2xl hover:shadow-lg transition-all duration-300 group"
          >
            ← Go Back
          </button>
        </div>

        {loading ? (
          <LoadingScreen />
        ) : mindMapData ? (
          <div className="overflow-x-auto">
            <MindMap data={mindMapData} />
          </div>
        ) : (
          <p className="text-center text-red-500">No mind map data available.</p>
        )}
      </div>
    </div>
  );
};

export default MindMapPage;
