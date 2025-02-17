import React from 'react';
import { Link } from 'react-router-dom';
import { FaStar, FaRegClock, FaUserAlt } from 'react-icons/fa'; // Importing icons from react-icons

const Course = ({ course }) => {
    const { id, courseName, bannerImage, rating, author, duration, price, discount, lessons, reviews, authorImage } = course;
    return (
        <div className="max-w-sm bg-white border border-gray-200 rounded-lg shadow-md overflow-hidden">
            <Link to={`/courses`} className="block overflow-hidden relative group">
                <img className="rounded-t-lg w-full h-48 object-cover transition-transform duration-500 ease-in-out transform group-hover:scale-110" src={bannerImage} alt={courseName} />
                <div className="absolute inset-0 bg-indigo-800 bg-opacity-0 group-hover:bg-opacity-60 transition duration-500 ease-in-out"></div>
            </Link>
            <div className="p-4">
                <div className="flex items-center mb-2">
                    <span className="text-yellow-500 mr-1"><FaStar /></span>
                    <span className="text-yellow-500 font-bold">{rating}</span>
                    <span className="text-gray-600 ml-1">({reviews})</span>
                </div>
                <Link to={`/courses`}>
                    <h5 className="text-xl font-bold tracking-tight text-gray-900">{courseName}</h5>
                </Link>
                <div className="flex items-center mt-2 mb-4 text-gray-700">
                    <span className="flex items-center mr-4">
                        <FaRegClock className="mr-1" /> {lessons} lesson
                    </span>
                    <span className="flex items-center mr-4">
                        <FaRegClock className="mr-1" /> {duration}
                    </span>
                    <span className="flex items-center">
                        <FaUserAlt className="mr-1" /> Expert
                    </span>
                </div>
                <div className="flex items-center">
                    <img className="w-8 h-8 rounded-full mr-2" src={authorImage} alt={author.name} />
                    <span className="text-gray-700">{author}</span>
                </div>
                <div className="flex items-center justify-between mt-4">
                    <span className="text-gray-400 line-through">${price}</span>
                    <span className="text-xl font-bold text-gray-900">${discount}</span>
                </div>
            </div>
        </div>
    );
};

export default Course;
