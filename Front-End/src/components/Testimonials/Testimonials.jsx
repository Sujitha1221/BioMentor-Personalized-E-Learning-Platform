import React from "react";
import {
  AcademicCapIcon,
  StarIcon,
  ChatBubbleLeftRightIcon,
} from "@heroicons/react/24/solid";

const testimonials = [
  {
    quote: "Helped me memorize complex biology terms effortlessly!",
    name: "University Student",
    icon: <AcademicCapIcon className="h-8 w-8 text-yellow-400" />,
  },
  {
    quote: "It really helped me summarize long texts for better understanding.",
    name: "Student who just completed A/L",
    icon: <ChatBubbleLeftRightIcon className="h-8 w-8 text-blue-400" />,
  },
  {
    quote: "ML-powered quizzes significantly improved my MCQ performance!",
    name: "A/L Biology Student",
    icon: <StarIcon className="h-8 w-8 text-green-400" />,
  },
  {
    quote: "A game-changer for structured answer evaluation in biology.",
    name: "A/L Biology Teacher",
    icon: <ChatBubbleLeftRightIcon className="h-8 w-8 text-blue-400" />,
  },
];

const Testimonials = () => {
  return (
    <div className="w-4/5 mx-auto p-6 text-center py-16 bg-gradient-to-b from-gray-900 to-gray-800 rounded-xl shadow-lg">
      <h2 className="text-3xl font-extrabold text-white mb-4">
        Empowering A/L Biology Students with ML
      </h2>
      <p className="text-lg text-gray-300 mb-10">
        Our ML-driven platform helps A/L Biology students enhance learning
        through smart memorization techniques, adaptive quizzes, text
        summarization, and AI-powered answer evaluation.
      </p>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {testimonials.map((testimonial, index) => (
          <div
            key={index}
            className="bg-gray-900 p-6 rounded-lg shadow-md transform transition hover:scale-105"
          >
            <div className="flex justify-center mb-4">{testimonial.icon}</div>
            <p className="text-white text-lg font-semibold">
              "{testimonial.quote}"
            </p>
            <p className="text-gray-400 mt-2">- {testimonial.name}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Testimonials;
