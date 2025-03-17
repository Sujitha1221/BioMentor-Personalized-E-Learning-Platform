import React from "react";
import HeroImage from "../../assets/image/hero.png";
import "./Hero.css";
import {
  AcademicCapIcon,
  ComputerDesktopIcon,
  PlayCircleIcon,
} from "@heroicons/react/24/solid";

const Hero = () => {
  return (
    <div className="w-4/5 mx-auto flex flex-col lg:flex-row items-center pt-20 pb-10">
      <div className="w-full lg:w-1/2">
        <h1 className="mb-4 text-4xl font-extrabold leading-none tracking-tight md:text-5xl lg:text-6xl text-white">
          Enhance Biology Learning with ML-Powered{" "}
          <span className="text-color">Tools</span>
        </h1>
        <p className="my-8 text-lg font-normal text-white lg:text-xl">
          Specially designed for A/L Biology students, our platform leverages
          cutting-edge ML to enhance vocabulary retention, effortlessly
          summarize long texts, master MCQ answering skills, and provide
          intelligent answers and evaluations for structured and essay-type
          questions.
        </p>
        <div className="flex flex-col md:flex-row">
          <a
            href="#top-categories"
            className="button-course outline-none font-medium rounded-lg px-8 py-4 text-center text-lg mb-2 md:mb-0 md:me-2"
          >
            Explore Features
          </a>
        </div>
        <div className="my-5 flex flex-col gap-5 md:flex-row md:gap-8">
          <p className="flex gap-2 text-white">
            <AcademicCapIcon className="h-6 w-6 text-white" />
            <span>Spaced Repetition</span>
          </p>
          <p className="flex gap-2 text-white">
            <PlayCircleIcon className="h-6 w-6 text-white" />
            <span>Abstractive Summarization</span>
          </p>
          <p className="flex gap-2 text-white">
            <ComputerDesktopIcon className="h-6 w-6 text-white" />
            <span>Adaptive MCQs</span>
          </p>
          <p className="flex gap-2 text-white">
            <ComputerDesktopIcon className="h-6 w-6 text-white" />
            <span>Answer Evaluation</span>
          </p>
        </div>
      </div>
      <div className="w-full lg:w-1/2">
        <img className="mx-auto hero-img" src={HeroImage} alt="Hero" />
      </div>
    </div>
  );
};

export default Hero;
