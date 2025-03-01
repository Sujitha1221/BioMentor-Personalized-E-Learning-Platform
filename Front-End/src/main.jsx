import React from 'react'
import ReactDOM from 'react-dom/client'
import './index.css'
import {
  createBrowserRouter,
  RouterProvider,
  Navigate,
} from "react-router-dom";
import Main from './components/Layout/Main.jsx';
import Home from './components/Home/Home.jsx';
import Courses from './components/Courses/Courses.jsx';
import Events from './components/Events/Events.jsx';
import Blogs from './components/Blogs/Blogs.jsx';
import About from './components/About/About.jsx';
import Contact from './components/Contact/Contact.jsx';
import Login from './components/Login/Login.jsx';
import SignUp from './components/SignUp/SignUp.jsx';
import QuestionAndAnsweringHomePage from './components/Q&A/QuestionAndAnsweringHomePage.jsx';
import QuestionAndAnsweringStudentDashboard from './components/Q&A/QuestionAndAnsweringStudentDashboard.jsx'
import QuestionAndAnsweringStudentHistory from './components/Q&A/QuestionAndAnsweringStudentHistory.jsx';
import QuestionAndAnsweringStudyMaterials from './components/Q&A/QuestionAndAnsweringStudyMaterials.jsx';

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
    path: "/home", // Parent route for authenticated pages
    element: <ProtectedRoute element={<Main />} />,
    children: [
      {
        index: true,
        element: <ProtectedRoute element={<Home />} />,
        loader: () => fetch('data.json'),
      },
      {
        path: "courses",
        element: <ProtectedRoute element={<Courses />} />,
        loader: () => fetch('data.json'),
      },
      {
        path: '/Q&A-home',
        element: <QuestionAndAnsweringHomePage></QuestionAndAnsweringHomePage>,
        loader: () => fetch('eventData.json')
      },
      {
        path: '/Q&A-dashboard',
        element: <QuestionAndAnsweringStudentDashboard></QuestionAndAnsweringStudentDashboard>,
        loader: () => fetch('eventData.json')
      },
      {
        path: '/Q&A-history',
        element: <QuestionAndAnsweringStudentHistory></QuestionAndAnsweringStudentHistory>,
        loader: () => fetch('eventData.json')
      },
      {
        path: '/Q&A-materials',
        element: <QuestionAndAnsweringStudyMaterials></QuestionAndAnsweringStudyMaterials>,
        loader: () => fetch('eventData.json')
      },
      {
        path: "blogs",
        element: <ProtectedRoute element={<Blogs />} />,
      },
      {
        path: "about",
        element: <ProtectedRoute element={<About />} />,
      },
      {
        path: "contact",
        element: <ProtectedRoute element={<Contact />} />,
      },
    ],
  },
]);

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
);
