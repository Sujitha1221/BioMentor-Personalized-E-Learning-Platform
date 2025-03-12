import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";
import { LOGIN_URL } from "../util/config";

const biologyElements = ["🧬", "🌱", "🔬", "🦠", "🧪", "🌿", "🧠"];

const SignUp = () => {
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const [floatingElements, setFloatingElements] = useState([]);
  const [educationLevel, setEducationLevel] = useState("");

  useEffect(() => {
    const newElements = Array.from({ length: 15 }).map(() => ({
      id: Math.random(),
      symbol:
        biologyElements[Math.floor(Math.random() * biologyElements.length)],
      x: Math.random() * 100,
      y: Math.random() * 100,
      speed: Math.random() * 4 + 2,
    }));
    setFloatingElements(newElements);
  }, []);

  const handleFormSubmit = async (event) => {
    event.preventDefault();
    setError("");

    const form = event.target;
    const username = form.username.value;
    const email = form.email.value;
    const password = form.password.value;
    const confirmPassword = form.confirmPassword.value;
    const fullName = form.fullName.value;

    if (!/^[A-Za-z ]{3,50}$/.test(fullName)) {
      setError(
        "Full name should contain only letters and spaces (3-50 characters)."
      );
      return;
    }

    if (!/^[a-zA-Z0-9_]{3,20}$/.test(username)) {
      setError("Username should be 3-20 characters long, without spaces.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match! Please try again.");
      return;
    }

    if (!educationLevel) {
      setError("Please select your education level.");
      return;
    }

    try {
      const response = await axios.post(`${LOGIN_URL}/register`, {
        username,
        email,
        password,
        full_name: fullName,
        education_level: educationLevel,
      });

      console.log("Sign Up successful", response.data);
      navigate("/");
    } catch (err) {
      console.error("Sign Up error", err.response);
      setError(err.response?.data?.detail || "Sign Up failed");
    }
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center bg-[#140342] p-4 overflow-hidden">
      {floatingElements.map((element) => (
        <span
          key={element.id}
          className="absolute text-3xl opacity-50"
          style={{
            left: `${element.x}%`,
            top: `${element.y}%`,
            animation: `floatAnimation ${element.speed}s infinite alternate ease-in-out`,
          }}
        >
          {element.symbol}
        </span>
      ))}

      <div className="relative z-10 bg-white/10 dark:bg-black/40 shadow-xl rounded-3xl p-10 w-full max-w-md border border-white/20 backdrop-blur-lg">
        <div className="flex flex-col items-center">
          <h1 className="text-4xl font-extrabold text-white text-center">
            🔬 BioMentor Sign Up
          </h1>
          <p className="text-gray-300 text-center mt-2">
            Join the world of Biology learning! 🌿🦠
          </p>
        </div>

        {error && <p className="text-red-400 text-center mt-3">{error}</p>}

        <form onSubmit={handleFormSubmit} className="mt-6">
          <div className="mb-4">
            <label className="block text-sm font-medium text-white">
              Full Name
            </label>
            <input
              type="text"
              name="fullName"
              className="w-full px-5 py-3 mt-1 bg-gray-100 dark:bg-gray-900 border border-gray-400 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#140342] dark:text-white transition-all duration-300 hover:scale-105"
              placeholder="Enter your full name (e.g., John Doe)"
              required
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-white">
              Username
            </label>
            <input
              type="text"
              name="username"
              className="w-full px-5 py-3 mt-1 bg-gray-100 dark:bg-gray-900 border border-gray-400 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#140342] dark:text-white transition-all duration-300 hover:scale-105"
              placeholder="Choose a username (e.g., johndoe_123)"
              required
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-white">
              Email
            </label>
            <input
              type="email"
              name="email"
              className="w-full px-5 py-3 mt-1 bg-gray-100 dark:bg-gray-900 border border-gray-400 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#140342] dark:text-white transition-all duration-300 hover:scale-105"
              placeholder="yourname@biomentor.com"
              required
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-white">
              Password
            </label>
            <input
              type="password"
              name="password"
              className="w-full px-5 py-3 mt-1 bg-gray-100 dark:bg-gray-900 border border-gray-400 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#140342] dark:text-white transition-all duration-300 hover:scale-105"
              placeholder="Create a password"
              required
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-white">
              Confirm Password
            </label>
            <input
              type="password"
              name="confirmPassword"
              className="w-full px-5 py-3 mt-1 bg-gray-100 dark:bg-gray-900 border border-gray-400 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#140342] dark:text-white transition-all duration-300 hover:scale-105"
              placeholder="Re-enter your password"
              required
            />
          </div>

          {/* Education Level Dropdown */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-white">
              Education Level
            </label>
            <select
              value={educationLevel}
              onChange={(e) => setEducationLevel(e.target.value)}
              className="w-full px-5 py-3 mt-1 bg-gray-100 dark:bg-gray-900 border border-gray-400 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#140342] dark:text-white transition-all duration-300 hover:scale-105"
              required
            >
              <option value="">Select your education level</option>
              <option value="Grade 12">Grade 12</option>
              <option value="Grade 13">Grade 13</option>
              <option value="A/L Candidate (This Year)">
                A/L Candidate (This Year)
              </option>
              <option value="Repeating A/L (2nd Attempt)">
                Repeating A/L (2nd Attempt)
              </option>
              <option value="Repeating A/L (3rd Attempt)">
                Repeating A/L (3rd Attempt)
              </option>
            </select>
          </div>

          <button
            type="submit"
            className="w-full mt-4 bg-[#140342] hover:bg-[#180452] text-white font-semibold py-3 rounded-xl transition-all duration-300 shadow-md hover:scale-105"
          >
            Sign Up
          </button>
        </form>

        <p className="text-center text-gray-300 mt-5">
          Already have an account?{" "}
          <Link to="/" className="text-[#00FF84] font-semibold hover:underline">
            Login here
          </Link>
        </p>
      </div>
    </div>
  );
};

export default SignUp;
