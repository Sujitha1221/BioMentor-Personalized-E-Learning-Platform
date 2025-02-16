import React from 'react';
import HeroImage from "../../assets/image/hero.png";
import './Hero.css';
import { AcademicCapIcon, ComputerDesktopIcon, PlayCircleIcon } from '@heroicons/react/24/solid';

const Hero = () => {
    return (
        <div className='w-4/5 mx-auto flex flex-col lg:flex-row items-center pt-20'>
            <div className='w-full lg:w-1/2'>
                <h1 className="mb-4 text-4xl font-extrabold leading-none tracking-tight md:text-5xl lg:text-6xl text-white">
                    Learn New Skills Online with Top <span className="text-color">Educators</span>
                </h1>
                <p className="my-8 text-lg font-normal text-white lg:text-xl">
                    Build skills with courses, certificates, and degrees online from
                    world-class universities and companies.
                </p>
                <div className='flex flex-col md:flex-row'>
                    <button type="button" className="button-join outline-none bg-slate-300 font-medium rounded-lg px-8 py-4 text-center text-lg mb-2 md:mb-0 md:me-2">
                        Join For Free
                    </button>
                    <button type="button" className="button-course outline-none font-medium rounded-lg px-8 py-4 text-center text-lg mb-2 md:mb-0 md:me-2">
                        Find Courses
                    </button>
                </div>
                <div className='my-5 flex flex-col gap-5 md:flex-row md:gap-8'>
                    <p className='flex gap-2 text-white'>
                        <AcademicCapIcon className="h-6 w-6 text-white" /><span>Over 12 million students</span>
                    </p>
                    <p className='flex gap-2 text-white'>
                        <PlayCircleIcon className="h-6 w-6 text-white" /><span>More than 60,000 courses</span>
                    </p>
                    <p className='flex gap-2 text-white'>
                        <ComputerDesktopIcon className="h-6 w-6 text-white" /><span>Learn anything online</span>
                    </p>
                </div>
            </div>
            <div className='w-full lg:w-1/2'>
                <img className='mx-auto hero-img' src={HeroImage} alt="Hero" />
            </div>
        </div>
    );
};

export default Hero;
