import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";
import { LOGIN_URL } from "../util/config";

const biologyElements = ["🧬", "🌱", "🔬", "🦠", "🧪", "🌿", "🧠"];

const Login = () => {
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const [floatingElements, setFloatingElements] = useState([]);

  useEffect(() => {
    // Generate random floating elements
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
    const email = form.email.value;
    const password = form.password.value;

    try {
      const response = await axios.post(
        `${LOGIN_URL}/login`,
        { email, password },
        { withCredentials: true }
      );
      const { access_token, refresh_token, username, user_id } = response.data;

      localStorage.setItem("token", access_token);
      localStorage.setItem("refresh_token", refresh_token);
      localStorage.setItem(
        "user",
        JSON.stringify({ email, username, user_id })
      );

      console.log("Login successful", response.data);

      navigate("/home");
    } catch (err) {
      console.error("Login error", err.response);
      setError(err.response?.data?.detail || "Login failed");
    }
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center bg-[#140342] p-4 overflow-hidden">
      {/* Floating Biology Elements Everywhere */}
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

      {/* DNA Double Helix Moving Across the Screen */}
      <div className="absolute top-0 left-1/2 transform -translate-x-1/2 animate-dnaMove">
        <div className="relative w-20 h-[500px]">
          {[...Array(15)].map((_, i) => (
            <span
              key={i}
              className="absolute w-3 h-3 bg-green-400 rounded-full shadow-lg"
              style={{
                left: `${i % 2 === 0 ? "0%" : "100%"}`,
                top: `${i * 7}%`,
              }}
            ></span>
          ))}
        </div>
      </div>

      {/* Glowing Radial Light Effects */}
      <div className="absolute inset-0 bg-radial-gradient from-[#140342] via-transparent to-transparent opacity-50"></div>

      {/* Login Card */}
      <div className="relative z-10 bg-white/10 dark:bg-black/40 shadow-xl rounded-3xl p-10 w-full max-w-md border border-white/20 backdrop-blur-lg">
        <div className="flex flex-col items-center">
          <h1 className="text-4xl font-extrabold text-white text-center">
            🔬 BioMentor Login
          </h1>
          <p className="text-gray-300 text-center mt-2">
            Enter your credentials to explore Biology! 🌿🦠
          </p>
        </div>

        {error && <p className="text-red-400 text-center mt-3">{error}</p>}

        <form onSubmit={handleFormSubmit} className="mt-6">
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
              placeholder="Enter your password"
              required
            />
          </div>

          <button
            type="submit"
            className="w-full mt-4 bg-[#140342] hover:bg-[#180452] text-white font-semibold py-3 rounded-xl transition-all duration-300 shadow-md hover:scale-105"
          >
            Login
          </button>
        </form>

        <p className="text-center text-gray-300 mt-5">
          Don't have an account?{" "}
          <Link
            to="/signup"
            className="text-[#00FF84] font-semibold hover:underline"
          >
            Sign up now
          </Link>
        </p>
      </div>

      {/* CSS for Floating Animation & DNA Animation */}
      <style>
        {`
                    @keyframes floatAnimation {
                        0% { transform: translateY(0px) rotate(0deg); }
                        100% { transform: translateY(20px) rotate(10deg); }
                    }

                    @keyframes dnaMove {
                        0% { transform: translateY(-100px) scale(1); }
                        50% { transform: translateY(100px) scale(1.1); }
                        100% { transform: translateY(-100px) scale(1); }
                    }

                    .animate-dnaMove {
                        animation: dnaMove 10s infinite ease-in-out;
                    }
                `}
      </style>
    </div>
  );
};

export default Login;
