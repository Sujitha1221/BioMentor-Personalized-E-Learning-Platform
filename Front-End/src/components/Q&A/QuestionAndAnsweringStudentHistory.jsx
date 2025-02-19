import React, { useState, useEffect } from "react";
import axios from "axios";
import LoadingScreen from "../LoadingScreen/LoadingScreen";
import { AiOutlineSearch, AiOutlineCopy, AiFillCheckCircle, AiOutlineDown, AiOutlineUp } from "react-icons/ai";

const QuestionAndAnsweringStudentHistory = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true); 
  const [searchQuery, setSearchQuery] = useState("");
  const [copiedIndex, setCopiedIndex] = useState(null);
  const [expandedIndex, setExpandedIndex] = useState(null);

  useEffect(() => {
    axios
      .post("http://127.0.0.1:8000/student-analytics", { student_id: "student123" })
      .then((response) => {
        setHistory(response.data.analytics.evaluations || []);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching student history:", error);
        setLoading(false);
      });
  }, []);

  const handleCopy = (text, index) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const toggleExpand = (index) => {
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  const filteredHistory = history.filter((item) =>
    item.question.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading) return <LoadingScreen />;

  return (
    <div className="container mx-auto p-6  md:mt-20">
      {/* <h1 className="text-3xl font-bold text-gray-800 mb-6 text-center">📜 Student Answer History</h1> */}
      <div className="relative w-full max-w-md mx-auto mb-6">
        <input
          type="text"
          placeholder="Search questions..."
          className="w-full pl-10 pr-12 py-3 border rounded-lg shadow-sm focus:ring-2 focus:ring-blue-400"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        <AiOutlineSearch className="absolute left-3 top-3 text-gray-500 text-lg" />
        {searchQuery && (
          <button
            className="absolute right-3 top-2 text-sm text-red-500 hover:underline"
            onClick={() => setSearchQuery("")}
          >
            Clear
          </button>
        )}
      </div>
      <div className="bg-white shadow-lg rounded-xl overflow-hidden">
        <h2 className="text-lg font-semibold px-6 py-4 bg-gray-100">📊 Answer History</h2>
        <div className="overflow-x-auto">
          <table className="w-full table-auto border-collapse">
            <thead>
              <tr className="bg-gray-200 text-gray-700 text-sm uppercase">
                <th className="py-3 px-6 text-left">#</th>
                <th className="py-3 px-6 text-left">Question</th>
                <th className="py-3 px-6 text-left">Student Answer</th>
                <th className="py-3 px-6 text-left">Model Answer</th>
                <th className="py-3 px-6 text-left">Expand</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-300">
              {filteredHistory.length > 0 ? (
                filteredHistory.map((item, index) => (
                  <React.Fragment key={index}>
                    <tr className="hover:bg-gray-100 transition cursor-pointer" onClick={() => toggleExpand(index)}>
                      <td className="py-4 px-6">{index + 1}</td>
                      <td className="py-4 px-6 font-medium text-gray-900 truncate max-w-xs">{item.question}</td>
                      <td className="py-4 px-6 text-gray-600 truncate max-w-xs">{item.user_answer}</td>
                      <td className="py-4 px-6 text-green-700 relative truncate max-w-xs">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleCopy(item.model_answer, index);
                          }}
                          className="absolute top-2 right-2 bg-gray-200 p-2 rounded-lg hover:bg-gray-300 transition-all flex items-center"
                        >
                          {copiedIndex === index ? (
                            <AiFillCheckCircle className="text-green-600 text-lg" />
                          ) : (
                            <AiOutlineCopy className="text-gray-700 text-lg" />
                          )}
                        </button>
                        <span className="block truncate w-[90%] pr-10">{item.model_answer}</span>
                      </td>
                      <td className="py-4 px-6 text-center">
                        <button className="text-gray-500 hover:text-gray-700">
                          {expandedIndex === index ? <AiOutlineUp /> : <AiOutlineDown />}
                        </button>
                      </td>
                    </tr>
                    {expandedIndex === index && (
                      <tr className="bg-gray-50">
                        <td colSpan="5" className="py-4 px-6 text-gray-700">
                          <div className="flex flex-col gap-2">
                            <p><span className="font-semibold text-gray-900">❓ Question:</span> {item.question}</p>
                            <p><span className="font-semibold text-gray-900">📝 Student Answer:</span> {item.user_answer}</p>
                            <p><span className="font-semibold text-gray-900">📌 Model Answer:</span> {item.model_answer}</p>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))
              ) : (
                <tr>
                  <td colSpan="5" className="text-center text-gray-500 py-4">No records found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default QuestionAndAnsweringStudentHistory;
