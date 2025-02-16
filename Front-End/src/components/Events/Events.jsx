import React from 'react';
import { useLoaderData } from 'react-router-dom';
import Event from '../Event/Event';

const Events = () => {
    const events = useLoaderData();

    return (
        <div className="events-page w-4/5 mx-auto mt-2 md:mt-24 mb-16">
            <h1 className="text-4xl font-bold mb-10 text-center">Upcoming Events</h1>
            <div className='grid sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8'>
                {events.map((event, index) => (
                    <Event
                        key={index}
                        event={event}
                    />
                ))}
            </div>

        </div>
    );
};

export default Events;