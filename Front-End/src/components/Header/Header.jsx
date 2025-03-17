import React, { useState, useEffect, useRef } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import ActiveLink from "../ActiveLink/ActiveLink";
import { FaUserCircle } from "react-icons/fa";
import { motion } from "framer-motion";
import logo from "../../../src/assets/Logo.png";
import "./Header.css";

const Header = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showLogoutModal, setShowLogoutModal] = useState(false); //  Logout modal state

  const dropdownRef = useRef(null);
  const navigate = useNavigate();
  const location = useLocation(); // Get current route

  // Check if user is logged in
  useEffect(() => {
    const token = localStorage.getItem("token");
    setIsLoggedIn(!!token);
  }, []);

  const handleLogout = () => {
    //  Remove all stored authentication details
    localStorage.removeItem("token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");

    setIsLoggedIn(false);
    setShowLogoutModal(false);
    navigate("/"); // Redirect to Home page after logout
  };

  const handleToggleMenu = () => {
    setMenuOpen(!menuOpen);
  };

  const handleToggleDropdown = () => {
    setDropdownOpen(!dropdownOpen);
  };

  const handleClickOutside = (event) => {
    if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
      setDropdownOpen(false);
    }
  };

  useEffect(() => {
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  // Hide header on the "/" route
  if (location.pathname === "/" || location.pathname === "/signup") {
    return null;
  }

  return (
    <>
      <nav className="navbar md:fixed top-0 left-0 z-10 w-full hero-bg z-20">
        <div className="w-4/5 flex flex-wrap items-center justify-between mx-auto py-4">
          {/* Logo - Left Aligned */}
          <div className="flex items-center space-x-4">
            <img src={logo} alt="Logo" className="h-16" />
            <motion.h1 className="text-3xl font-extrabold tracking-tight leading-tight text-transparent bg-clip-text bg-gradient-to-r from-[#00FF84] to-[rgb(100,181,246)] drop-shadow-lg px-4 sm:px-0">
              Bio Mentor
            </motion.h1>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={handleToggleMenu}
            type="button"
            className="inline-flex items-center p-2 w-10 h-10 justify-center text-sm text-gray-500 rounded-lg md:hidden hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200 dark:text-gray-400 dark:hover:bg-gray-700 dark:focus:ring-gray-600"
            aria-controls="navbar-default"
            aria-expanded={menuOpen}
          >
            <span className="sr-only">Open main menu</span>
            <svg
              className="w-5 h-5"
              aria-hidden="true"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 17 14"
            >
              <path
                stroke="currentColor"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M1 1h15M1 7h15M1 13h15"
              />
            </svg>
          </button>

          {/* Navigation Menu */}
          <div
            className={`${
              menuOpen ? "block" : "hidden"
            } w-full md:flex md:flex-1 md:justify-center`}
            id="navbar-default"
          >
            <ul className="font-medium text-white flex flex-col gap-3 justify-center p-4 md:p-0 mt-4 md:flex-row md:space-x-8 rtl:space-x-reverse md:mt-0 md:border-0 items-center">
              <li>
                <ActiveLink to="/home">Home</ActiveLink>
              </li>
              <li>
                <ActiveLink to="/MCQ-home">MCQ</ActiveLink>
              </li>
              <li>
                <ActiveLink to={"/Q&A-home"}>Q & A</ActiveLink>
              </li>
              <li>
                <ActiveLink to="/blogs">Vocabulary</ActiveLink>
              </li>
              <li>
                <ActiveLink to="/summarize">Summarize</ActiveLink>
              </li>

              {/* User Icon (Only in Mobile Menu) */}
              <li className="block">
                <div className="relative" ref={dropdownRef}>
                  <button
                    onClick={handleToggleDropdown}
                    className={`flex items-center space-x-2 transition duration-200 ${
                      dropdownOpen ? "text-[rgb(100,181,246)]" : "text-white"
                    }`}
                  >
                    <FaUserCircle className="w-8 h-8" />
                    <span className="font-medium md:hidden">Account</span>
                  </button>
                  {dropdownOpen && (
                    <div className="absolute left-0 mt-2 w-48 bg-white rounded-md shadow-lg py-2 z-20">
                      <Link
                        to="/profile"
                        className="block px-4 py-2 text-gray-700 hover:bg-gray-100"
                      >
                        My Profile
                      </Link>
                      <button
                        onClick={() => setShowLogoutModal(true)}
                        className="block w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-100 hover:text-[#00FF84] focus:outline-none"
                      >
                        Logout
                      </button>
                    </div>
                  )}
                </div>
              </li>
            </ul>
          </div>
        </div>
      </nav>
      {/*  Logout Confirmation Modal */}
      {showLogoutModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-gray-800 bg-opacity-50 z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg text-center">
            <h2 className="text-lg font-semibold text-gray-800">
              Are you sure you want to log out?
            </h2>
            <div className="mt-4 flex justify-center space-x-4">
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
              >
                Yes, Logout
              </button>
              <button
                onClick={() => setShowLogoutModal(false)}
                className="px-4 py-2 bg-gray-300 text-gray-800 rounded hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Header;
