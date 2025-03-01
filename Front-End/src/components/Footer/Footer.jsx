import React from 'react';
import { Link } from 'react-router-dom';

const Footer = () => {
      // Hide header on the "/" route
  if (location.pathname === "/" || location.pathname === "/signup") {
    return null;
  }
  
    return (
        <footer className="bottom-0 left-0 z-20 w-full hero-bg py-4">
            <div className="mx-auto w-full max-w-screen-xl">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 px-4 py-4">
                    {/* Description - Left Side */}
                    <div className="text-white">
                        <h2 className="text-lg font-bold mb-2">Empowering Learning, One Click at a Time</h2>
                        <p className="text-gray-400 text-sm">
                            Bio Mentor is an e-learning platform designed to help A/L Biology students in Sri Lanka master complex concepts with ease. It offers interactive tools like adaptive quizzes, digital flashcards, and automated text summarization for a personalized learning experience. With real-time feedback and dynamic assessments, Bio Mentor helps students bridge knowledge gaps, enhance retention, and achieve academic success.
                        </p>
                    </div>

                    {/* Links - Right Side */}
                    <div className="text-center md:text-right">
                        <h2 className="mb-4 text-sm font-semibold uppercase text-white">Quick Links</h2>
                        <ul className="text-gray-500 dark:text-gray-400 text-sm font-medium">
                            <li className="mb-2">
                                <Link to="/about" className="hover:underline">MCQ</Link>
                            </li>
                            <li className="mb-2">
                                <Link to="/Q&A-home" className="hover:underline">Q & A</Link>
                            </li>
                            <li className="mb-2">
                                <Link to="/home" className="hover:underline">Vocabulary</Link>
                            </li>
                            <li className="mb-2">
                                <Link to="/blogs" className="hover:underline">Summarize</Link>
                            </li>
                        </ul>
                    </div>
                </div>

                {/* Copyright - Center aligned on mobile, left on desktop */}
                <div className="px-4 py-3 flex flex-col items-center md:flex-row md:justify-between">
                    <span className="text-xs text-gray-500 dark:text-gray-300 text-center md:text-left">
                        © 2024 <Link to="/">E-Learning</Link>. All Rights Reserved.
                    </span>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
