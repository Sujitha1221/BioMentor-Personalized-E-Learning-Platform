import React from 'react';
import Course from '../Course/Course';

const TopCourse = ({displayCourses}) => {
    return (
        <div className='w-3/4 mx-auto mt-32 mb-10'>
            <h1 className='text-4xl font-semibold text-center'>Our Most Popular Courses</h1>
            <p className='mb-10 mt-5 text-center'>10,000+ unique online course list designs</p>
            <div className='grid sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8'>
                {
                    displayCourses.map(course => (
                        <Course key={course.id} course={course} />
                    ))
                }
            </div>
        </div>
    );
};

export default TopCourse;