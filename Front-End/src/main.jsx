import React from 'react'
import ReactDOM from 'react-dom/client'
import './index.css'
import {
  createBrowserRouter,
  RouterProvider,
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

const router = createBrowserRouter([  
  {
    path: "/",
    element: <Main></Main>,
    children: [
      {
        path: '/',
        element: <Home></Home>,
        loader: () => fetch('data.json'),
      },
      {
        path: '/courses',
        element: <Courses></Courses>,
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
        path: '/blogs',
        element: <Blogs></Blogs>
      },
      {
        path: '/about',
        element: <About></About>
      },
      {
        path: '/contact',
        element: <Contact></Contact>
      },
      {
        path: '/login',
        element: <Login></Login>
      },
      {
        path: '/signup',
        element: <SignUp></SignUp>
      },
    ],
  },
]);

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
)
