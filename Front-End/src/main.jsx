import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import {
  createBrowserRouter,
  RouterProvider,
  Navigate,
} from "react-router-dom";
import Main from "./components/Layout/Main.jsx";
import Home from "./components/Home/Home.jsx";
import Login from "./components/Login/Login.jsx";
import SignUp from "./components/SignUp/SignUp.jsx";
import QuestionAndAnsweringHomePage from "./components/Q&A/QuestionAndAnsweringHomePage.jsx";
import QuestionAndAnsweringStudentDashboard from "./components/Q&A/QuestionAndAnsweringStudentDashboard.jsx";
import QuestionAndAnsweringStudentHistory from "./components/Q&A/QuestionAndAnsweringStudentHistory.jsx";
import QuestionAndAnsweringStudyMaterials from "./components/Q&A/QuestionAndAnsweringStudyMaterials.jsx";
import MindMapPage from "./components/Q&A/models/MindMapPage.jsx";
import Summarization from "./components/Summarization/Summarization.jsx";
import MCQHomePage from "./components/MCQ/MCQHomePage.jsx";
import QuizPage from "./components/MCQ/QuizPage.jsx";
import QuizResults from "./components/MCQ/QuizResults.jsx";
import QuizHistory from "./components/MCQ/QuizHistory.jsx";
import PerformanceDashboard from "./components/MCQ/PerformanceDashboard.jsx";
import TopicBasedQuizzes from "./components/MCQ/TopicBasedQuiz/TopicBasedQuizzes.jsx";
import TopicBasedQuizPage from "./components/MCQ/TopicBasedQuiz/TopicBasedQuizPage.jsx";
import ScrollToTop from "./components/ScrollToTop/ScrollToTop.jsx";
import TopicBasedQuizResults from "./components/MCQ/TopicBasedQuiz/TopicBasedQuizResults.jsx";

// Protected Route Component
const ProtectedRoute = ({ element }) => {
  const isAuthenticated = localStorage.getItem("token"); // Check if logged in
  return isAuthenticated ? element : <Navigate to="/" replace />;
};

const router = createBrowserRouter([
  {
    path: "/", // Login Page (Public)
    element: <Login />,
  },
  {
    path: "/signup", // Signup Page (Public)
    element: <SignUp />,
  },
  {
    path: "/", // Parent route for authenticated pages
    element: (
      <>
        <ScrollToTop /> {/*Ensures page scrolls to top on route change */}
        <ProtectedRoute element={<Main />} />
      </>
    ),
    children: [
      {
        index: true,
        path: "home",
        element: <ProtectedRoute element={<Home />} />,
      },
      {
        path: "Q&A-home",
        element: <ProtectedRoute element={<QuestionAndAnsweringHomePage />} />,
      },
      {
        path: "Q&A-dashboard",
        element: (
          <ProtectedRoute element={<QuestionAndAnsweringStudentDashboard />} />
        ),
      },
      {
        path: "Q&A-history",
        element: (
          <ProtectedRoute element={<QuestionAndAnsweringStudentHistory />} />
        ),
      },
      {
        path: "Q&A-materials",
        element: (
          <ProtectedRoute element={<QuestionAndAnsweringStudyMaterials />} />
        ),
      },
      {
        path: "mind-map",
        element: (
          <ProtectedRoute element={<MindMapPage />} />
        ),
      },
      {
        path: "summarize",
        element: <ProtectedRoute element={<Summarization />} />,
      },
      {
        path: "MCQ-home",
        element: <ProtectedRoute element={<MCQHomePage />} />,
      },
      {
        path: "quiz-page",
        element: <ProtectedRoute element={<QuizPage />} />,
      },
      {
        path: "quiz-results",
        element: <ProtectedRoute element={<QuizResults />} />,
      },
      {
        path: "quiz-history",
        element: <ProtectedRoute element={<QuizHistory />} />,
      },
      {
        path: "performance-dashboard",
        element: <ProtectedRoute element={<PerformanceDashboard />} />,
      },
      {
        path: "topic-quizzes",
        element: <ProtectedRoute element={<TopicBasedQuizzes />} />,
      },
      {
        path: "topic_quiz",
        element: <ProtectedRoute element={<TopicBasedQuizPage />} />,
      },
      {
        path: "topic_quiz/results",
        element: <ProtectedRoute element={<TopicBasedQuizResults />} />,
      },
    ],
  },
]);

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
