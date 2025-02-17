import React from 'react';
import { Link } from 'react-router-dom';
import { MapPinIcon, CalendarDaysIcon } from '@heroicons/react/24/solid';

const Event = ({ event }) => {
    const { title, date, location, description, banner } = event;

    return (
        <div className="max-w-sm bg-white border border-gray-200 rounded-lg shadow-md overflow-hidden">
            <Link to={`/events`} className="block overflow-hidden relative group">
                <img className="rounded-t-lg w-full h-48 object-cover transition-transform duration-500 ease-in-out transform group-hover:scale-110" src={banner} alt={title} />
                <div className="absolute inset-0 bg-indigo-800 bg-opacity-0 group-hover:bg-opacity-60 transition duration-500 ease-in-out"></div>
            </Link>
            <div className="p-4">
                <Link to={`/events`}>
                    <h5 className="text-xl font-bold tracking-tight text-gray-900">{title}</h5>
                </Link>
                <div className="mt-2 mb-4 text-gray-700">
                    <span className="flex items-center mr-3 mb-5">
                        <MapPinIcon className="size-6 text-blue-500" /> {location}
                    </span>
                    <span className="flex items-center mr-4">
                        <CalendarDaysIcon className="size-6 text-blue-500 mr-1" /> {date}
                    </span>
                </div>
                <button
                    type="submit"
                    className="text-white button-join outline-none font-bold rounded-lg text-md w-full px-5 py-2.5 text-center"
                >
                    Buy Now
                </button>
            </div>
        </div>
    );
};

export default Event;