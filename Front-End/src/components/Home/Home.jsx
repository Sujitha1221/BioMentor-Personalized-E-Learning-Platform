import React from 'react';
import "./Home.css";
import Hero from '../Hero/Hero';
import TrustedBrand from '../TrustedBrand/TrustedBrand';
import TopCategories from '../TopCategories/TopCategories';
import { useLoaderData } from 'react-router-dom';
import TopCourse from '../TopCourse/TopCourse';
import PromoSection from '../PromoSection/PromoSection';

const Home = () => {
    // Fetch courses after delay
    const courses = useLoaderData();
    const displayCourses = courses.slice(0, 8);

    return (
        <div>
            <div className='hero-bg-img mt-0 md:mt-14'>
                <Hero />
            </div>
            <div className='my-20'>
                <TrustedBrand />
            </div>
            <div className='my-20'>
                <TopCategories />
            </div>
            <div className='my-20'>
                <TopCourse displayCourses={displayCourses} />
            </div>
            <div className='my-20'>
                <PromoSection />
            </div>
        </div>
    );
};

export default Home;
