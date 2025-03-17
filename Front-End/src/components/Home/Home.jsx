import React from "react";
import "./Home.css";
import Hero from "../Hero/Hero";
import TrustedBrand from "../TrustedBrand/TrustedBrand";
import TopCategories from "../TopCategories/TopCategories";
import PromoSection from "../PromoSection/PromoSection";

const Home = () => {
  return (
    <div>
      <div className="hero-bg-img mt-0 md:mt-14">
        <Hero />
      </div>
      <div className="my-20">
        <TrustedBrand />
      </div>
      <div id="top-categories" className="my-20">
        <TopCategories />
      </div>
      <div className="my-20">
        <PromoSection />
      </div>
    </div>
  );
};

export default Home;
