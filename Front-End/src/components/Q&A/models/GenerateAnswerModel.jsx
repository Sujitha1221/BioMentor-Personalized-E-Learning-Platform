import React, { useState } from "react";
import axios from "axios";
import ReactLoading from "react-loading";
import { FaCopy, FaCheck, FaInfoCircle, FaTimes } from "react-icons/fa";
import { ArrowLeft, Sparkles } from "lucide-react";
import ModalLoadingScreen from "../../LoadingScreen/ModalLoadingScreen";
import AlertMessage from "../../Alert/Alert";
import { QA_URL } from "../../util/config";

const GenerateAnswerModel = ({ onBack }) => {
  const [question, setQuestion] = useState("");
  const [questionType, setQuestionType] = useState("structured");
  const [answer, setAnswer] = useState("");
  const [relatedWebsites, setRelatedWebsites] = useState([]);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [showLinks, setShowLinks] = useState(false);
  const [alert, setAlert] = useState({message:"", type:""});
  const [studentId,setStudentId] = useState("");

  const handleGenerateAnswer = async () => {
    if (!question) {
      //alert("Please enter a question!");
      setAlert({message:"Please enter a question!", type:"warning"});
      return;
    }

    let storedStudentId = localStorage.getItem("user");
    if (storedStudentId) {
      storedStudentId = JSON.parse(storedStudentId).email;
      setStudentId(storedStudentId);
    }

    setLoading(true);
    setAnswer("");
    setRelatedWebsites([]);
    setShowLinks(false);

    try {
      const response = await axios.post(`${QA_URL}/generate-answer`, {
        student_id: storedStudentId,
        question,
        type: questionType,
      });

      setAnswer(response.data.answer);
      setRelatedWebsites(response.data.related_websites || []);
    } catch (error) {
      console.error("Error generating answer:", error.response.data.detail);
      setAlert({message:"Error generating answer: " + error.response.data.detail, error, type:"error"});
      //alert("Failed to generate answer. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (answer) {
      navigator.clipboard.writeText(answer);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const toggleLinks = () => {
    setShowLinks(!showLinks);
  };

  return (
    <>
    {alert.message && <AlertMessage message={alert.message} type={alert.type} onClose={() => setAlert({ message: "", type: "" })} />}
    <div className="space-y-6">
      <div className="bg-gray-100 p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Generate Answer</h3>

        <div className="mb-4">
          <label className="block text-gray-700 font-medium mb-2">Question</label>
          <input
            type="text"
            placeholder="Enter your question..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            disabled={loading}
            className="w-full border border-gray-300 p-3 rounded-lg focus:ring-2 focus:ring-blue-400"
          />
        </div>

        <div className="mb-4">
          <label className="block text-gray-700 font-medium mb-2">Question Type</label>
          <select
            value={questionType}
            onChange={(e) => setQuestionType(e.target.value)}
            disabled={loading}
            className="w-full border border-gray-300 p-3 rounded-lg bg-white focus:ring-2 focus:ring-blue-400"
          >
            <option value="structured">Structured</option>
            <option value="essay">Essay</option>
          </select>
        </div>

        <div className="mt-6">
          <label className="block text-gray-700 font-medium mb-2">Generated Answer:</label>
          <div className="relative">
            <textarea
              value={answer}
              readOnly
              className="w-full border border-gray-300 p-3 pr-16 rounded-lg bg-gray-100 text-gray-800 h-32 resize-none focus:ring-2 focus:ring-gray-300"
            />
            <button
              onClick={handleCopy}
              className="absolute top-2 right-2 bg-gray-300 p-2 rounded-lg hover:bg-gray-400 transition-all flex items-center"
            >
              {copied ? <FaCheck className="text-green-600" /> : <FaCopy className="text-gray-700" />}
            </button>
            <button
              onClick={toggleLinks}
              className="absolute top-2 right-14 bg-gray-300 p-2 rounded-lg hover:bg-gray-400 transition-all flex items-center"
            >
              <FaInfoCircle className="text-gray-700" />
            </button>
            {copied && (
              <div className="absolute top-[-30px] right-0 bg-green-500 text-white text-xs px-3 py-1 rounded-lg shadow-md transition-opacity animate-fade-in-out">
                Copied!
              </div>
            )}

            {showLinks && relatedWebsites.length > 0 && (
              <div className="fixed inset-0 flex items-center justify-center z-50">
                <div
                  className="absolute inset-0 bg-black opacity-50"
                  onClick={toggleLinks}
                ></div>
                <div className="relative bg-white border border-gray-200 p-6 rounded-xl shadow-lg w-full max-w-xs sm:max-w-md md:max-w-lg z-20">
                  <button
                    onClick={toggleLinks}
                    className="absolute top-2 right-2 text-gray-500 hover:text-gray-700"
                  >
                    <FaTimes className="w-6 h-6" />
                  </button>
                  <h4 className="text-xl font-bold text-gray-900 mb-4">Related Websites</h4>
                  <ul className="space-y-2">
                    {relatedWebsites.map((link, index) => (
                      <li key={index}>
                        <a
                          href={link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="block text-blue-600 hover:text-blue-800 transition-colors text-sm"
                        >
                          {link}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        </div>

        {loading && (
          <ModalLoadingScreen />
        )}

        <div className="flex flex-wrap justify-between gap-4 mt-4 w-full">
          <button
            className="flex-1 md:flex-none inline-flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#140342] text-white bg-[#140342] font-semibold rounded-lg 
      transition-transform duration-300 hover:scale-105 hover:bg-[#32265a]"
            disabled={loading}
            onClick={onBack}
          >
            <ArrowLeft size={20} /> Back
          </button>
          <button
            onClick={handleGenerateAnswer}
            disabled={loading}
            className="flex-1 md:flex-none inline-flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#00FF84] text-[#140342] bg-[#00FF84] font-semibold rounded-lg 
      transition-transform duration-300 hover:scale-105 hover:bg-[#00cc70]"
          >
            <Sparkles size={20} /> Generate Answer
          </button>
        </div>

      </div>
    </div>
    </>
  );
};

export default GenerateAnswerModel;