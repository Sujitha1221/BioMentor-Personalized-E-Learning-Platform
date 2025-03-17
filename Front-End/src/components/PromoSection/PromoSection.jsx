import React from "react";
import elearning from "../../assets/image/e-learning.jpg";

const PromoSection = () => {
  return (
    <div className="flex justify-center items-center">
      <div className="w-3/4 mx-auto px-4 py-12 flex flex-col-reverse md:flex-row items-center justify-between">
        <div className="md:w-1/2">
          <h2 className="text-4xl font-bold mb-4">
            <span className="text-color font-bold">
              Master ML-Powered Learning
            </span>
          </h2>
          <p className="text-gray-600 mb-6">
            Our platform is specially designed to help A/L Biology students
            improve retention, simplify learning, and excel in exams.
          </p>
          <ul className="mb-6 space-y-3 text-gray-600">
            <li className="flex items-center">
              <svg
                className="w-6 h-6 text-purple-600 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M5 13l4 4L19 7"
                ></path>
              </svg>
              Enhancing Biology Vocabulary through Digital Flashcards and Spaced
              Repetition
            </li>
            <li className="flex items-center">
              <svg
                className="w-6 h-6 text-purple-600 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M5 13l4 4L19 7"
                ></path>
              </svg>
              Abstractive Summarization with Voice Output
            </li>
            <li className="flex items-center">
              <svg
                className="w-6 h-6 text-purple-600 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M5 13l4 4L19 7"
                ></path>
              </svg>
              Adaptive MCQ Quiz Platform which creates questions based on user's
              performance
            </li>
            <li className="flex items-center">
              <svg
                className="w-6 h-6 text-purple-600 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M5 13l4 4L19 7"
                ></path>
              </svg>
              ML-Based Answer Evaluation for Biology Structured and Essay
              Questions
            </li>
          </ul>
          <button className="button-join text-white py-2 px-10 rounded-lg w-full sm:w-auto focus:outline-none">
            Join Free
          </button>
        </div>
        <div className="mt-8 md:mt-0 md:ml-8">
          <img
            src={elearning}
            alt="AI-Powered Learning"
            className="w-full max-w-md rounded-lg"
          />
        </div>
      </div>
    </div>
  );
};

export default PromoSection;
