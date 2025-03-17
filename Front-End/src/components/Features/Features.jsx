import React from "react";
import icon1 from "../../assets/image/flash_cards.png";
import icon2 from "../../assets/image/memo_4836957.png";
import icon3 from "../../assets/image/mcq.png";
import icon4 from "../../assets/image/qa.png";
import "./Features.css";
import { Link } from "react-router-dom";

const Features = () => {
  return (
    <div className="w-2/3 mx-auto mt-20">
      <div className="text-center">
        <h1 className="text-4xl font-bold mt-5">
          Explore ML-Powered Biology Learning
        </h1>
        <p className="text-gray-800 mt-5">
          Specially designed for A/L Biology students, our platform offers
          intelligent tools to enhance learning through ML-driven techniques.
        </p>
      </div>
      <div className="flex flex-wrap justify-center gap-8 mt-20">
        <Link
          className="category w-full sm:w-1/2 lg:w-1/6 bg-slate-200 py-5 px-3 rounded-lg"
          to="/spaced-repetition"
        >
          <div className="flex justify-center flex-col">
            <div className="bg-white p-4 rounded-full mx-auto mt-5">
              <img src={icon1} alt="" />
            </div>
            <p className="text-center text-xl mt-5">
              Flash cards and Spaced Repetition
            </p>
            <p className="text-center text-gray-500 text-sm mt-5">
              Boost Biology Vocabulary
            </p>
          </div>
        </Link>
        <Link
          className="category w-full sm:w-1/2 lg:w-1/6 bg-slate-200 py-5 px-3 rounded-lg"
          to="/summarize"
        >
          <div className="flex justify-center flex-col">
            <div className="bg-white p-4 rounded-full mx-auto mt-5">
              <img src={icon2} alt="" />
            </div>
            <p className="text-center text-xl mt-5">
              Text and Topic based Summarization
            </p>
            <p className="text-center text-gray-500 text-sm mt-5">
              Simplify Complex Topics
            </p>
          </div>
        </Link>
        <Link
          className="category w-full sm:w-1/2 lg:w-1/6 bg-slate-200 py-5 px-3 rounded-lg"
          to="/MCQ-home"
        >
          <div className="flex justify-center flex-col">
            <div className="bg-white p-4 rounded-full mx-auto mt-5">
              <img src={icon3} alt="" />
            </div>
            <p className="text-center text-xl mt-5">
              Adaptive MCQs based on Performance
            </p>
            <p className="text-center text-gray-500 text-sm mt-5">
              Improve Answering Skills
            </p>
          </div>
        </Link>
        <Link
          className="category w-full sm:w-1/2 lg:w-1/6 bg-slate-200 py-5 px-3 rounded-lg"
          to="/Q&A-home"
        >
          <div className="flex justify-center flex-col">
            <div className="bg-white p-4 rounded-full mx-auto mt-5">
              <img src={icon4} alt="" />
            </div>
            <p className="text-center text-xl mt-5">
              Question and Answer Evaluation
            </p>
            <p className="text-center text-gray-500 text-sm mt-5">
              Assess Structured & Essay Answers
            </p>
          </div>
        </Link>
      </div>
    </div>
  );
};

export default Features;
