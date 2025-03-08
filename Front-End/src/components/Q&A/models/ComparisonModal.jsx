import React, { useState } from "react";
import ReactLoading from "react-loading";
import { FaTimes, FaCopy, FaInfoCircle, FaCheck } from "react-icons/fa";
import { XIcon } from "lucide-react";

const ComparisonModal = ({
  showModal,
  loading,
  feedback,
  modelAnswer,
  answer,
  relatedWebsites = [],
  onClose
}) => {
  const [copied, setCopied] = useState(false);
  const [showLinks, setShowLinks] = useState(false);

  if (!showModal) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(modelAnswer);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const toggleLinks = () => {
    console.log("Toggling links modal:", !showLinks);
    setShowLinks(!showLinks);
  };

  return (
    <>
      <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 p-4">
        <div className="bg-white w-full max-w-lg h-[500px] rounded-lg shadow-lg flex flex-col relative">
          {loading && (
            <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-80 rounded-lg">
              <ReactLoading type="spin" color="#4f46e5" height={50} width={50} />
            </div>
          )}

          <div className="p-4 border-b flex justify-between items-center">
            <h3 className="text-xl font-bold text-gray-800">Comparison Result</h3>
            <button onClick={onClose} className="text-gray-600 hover:text-gray-900" disabled={loading}>
              <XIcon className="w-6 h-6" />
            </button>
          </div>

          <div className="p-4 flex-1 overflow-y-auto">
            <div className="mb-4">
              <h4 className="text-md font-semibold text-gray-700">Your Answer:</h4>
              <p className="bg-gray-100 p-3 rounded-lg text-gray-800">{answer}</p>
            </div>

            <div className="relative">
              <textarea
                value={modelAnswer}
                readOnly
                className="w-full border border-gray-300 p-3 pr-16 rounded-lg bg-gray-100 text-gray-800 h-32 resize-none focus:ring-2 focus:ring-gray-300"
              />
              <div className="absolute top-2 right-2 flex space-x-2">
                <button onClick={toggleLinks} className="bg-gray-300 p-2 rounded-lg hover:bg-gray-400 transition-all flex items-center">
                  <FaInfoCircle className="text-gray-700" />
                </button>
                <button onClick={handleCopy} className="bg-gray-300 p-2 rounded-lg hover:bg-gray-400 transition-all flex items-center">
                  {copied ? <FaCheck className="text-green-600" /> : <FaCopy className="text-gray-700" />}
                </button>
              </div>
              {copied && (
                <div className="absolute top-[-30px] right-0 bg-green-500 text-white text-xs px-3 py-1 rounded-lg shadow-md transition-opacity animate-fade-in-out">
                  Copied!
                </div>
              )}
            </div>

            <div className="mb-4">
              <h4 className="text-md font-semibold text-gray-700">Feedback:</h4>
              {feedback && (
                <div className="bg-blue-100 p-3 rounded-lg text-blue-800">
                  <p><strong>Final Score:</strong> {feedback.final_score}</p>
                  <p><strong>Semantic Score:</strong> {feedback.semantic_score}</p>
                  <p><strong>TF-IDF Score:</strong> {feedback.tfidf_score}</p>
                  <p><strong>Jaccard Score:</strong> {feedback.jaccard_score}</p>
                  <p><strong>Grammar Score:</strong> {feedback.grammar_score}</p>
                  <p><strong>Missing Keywords:</strong> {feedback.feedback?.missing_keywords.join(", ") || "None"}</p>
                  <p><strong>Extra Keywords:</strong> {feedback.feedback?.extra_keywords.join(", ") || "None"}</p>
                  <p><strong>Grammar Suggestions:</strong> {feedback.feedback?.grammar_suggestions.length > 0 ? feedback.feedback.grammar_suggestions.join(", ") : "No grammar issues detected."}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {showLinks && (
        <div className="fixed inset-0 flex items-center justify-center z-50">
          <div className="absolute inset-0 bg-black opacity-50" onClick={toggleLinks}></div>
          <div className="relative bg-white border border-gray-200 p-6 rounded-xl shadow-lg w-full max-w-xs sm:max-w-md md:max-w-lg z-20">
            <button onClick={toggleLinks} className="absolute top-2 right-2 text-gray-500 hover:text-gray-700">
              <FaTimes className="w-6 h-6" />
            </button>
            <h4 className="text-xl font-bold text-gray-900 mb-4">Related Websites</h4>
            <ul className="space-y-2">
              {relatedWebsites.length > 0 ? (
                relatedWebsites.map((link, index) => (
                  <li key={index}>
                    <a href={link} target="_blank" rel="noopener noreferrer" className="block text-blue-600 hover:text-blue-800 transition-colors text-sm">
                      {link}
                    </a>
                  </li>
                ))
              ) : (
                <p className="text-gray-600">No related websites available.</p>
              )}
            </ul>
          </div>
        </div>
      )}
    </>
  );
};

export default ComparisonModal;
