import React, { useRef } from "react";
import Hero from "./Hero";
import SummarizeDocument from "./SummarizeDocument";
import TopicSummary from "./TopicSummary";
import GenerateNotes from "./GenerateNotes";

const Summarization = () => {
  const summarizeRef = useRef(null);
  const topicSummaryRef = useRef(null); // Ref for TopicSummary

  const scrollToSummarize = () => {
    if (summarizeRef.current) {
      const yOffset = -80;
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

      {/* Sections */}
      <div ref={summarizeRef} className="mt-10">
        <SummarizeDocument />
      </div>

      {/* Add ref to Topic Summary */}
      <div ref={topicSummaryRef} className="mt-10">
        <TopicSummary />
      </div>

      <div ref={topicSummaryRef} className="mt-10">
        <GenerateNotes />
      </div>
    </div>
  );
};

export default Summarization;
