import React, { useRef } from "react";
import Hero from "./Hero";
import SummarizeDocument from "./SummarizeDocument";

const Summarization = () => {
  const summarizeRef = useRef(null);

  const scrollToSummarize = () => {
    if (summarizeRef.current) {
      const yOffset = -80; // Adjust this value based on your navbar height
      const y =
        summarizeRef.current.getBoundingClientRect().top +
        window.scrollY +
        yOffset;

      window.scrollTo({ top: y, behavior: "smooth" });
    }
  };

  return (
    <div className="bg-gray-100">
      {/* Pass scroll function to Hero */}
      <Hero scrollToSummarize={scrollToSummarize} />

      {/* Add a slight top margin to avoid cut-off */}
      <div ref={summarizeRef} className="mt-20">
        <SummarizeDocument />
      </div>
    </div>
  );
};

export default Summarization;
