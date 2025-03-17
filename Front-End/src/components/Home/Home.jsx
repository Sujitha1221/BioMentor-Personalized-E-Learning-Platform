import React from "react";
import "./Home.css";
import Hero from "../Hero/Hero";
import Testimonials from "../Testimonials/Testimonials";
import Features from "../Features/Features";
import PromoSection from "../PromoSection/PromoSection";

const Home = () => {
  return (
    <div>
      <div className="hero-bg-img mt-0 md:mt-14">
        <Hero />
      </div>
      <div className="my-20">
        <Testimonials />
      </div>
      <div id="top-categories" className="my-20">
        <Features />
      </div>
      <div className="my-20">
        <PromoSection />
      </div>
    </div>
  );
};

export default Home;
