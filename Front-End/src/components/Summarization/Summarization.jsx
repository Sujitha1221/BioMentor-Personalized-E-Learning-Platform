import React, { useRef } from "react";
import Hero from "./Hero";
import SummarizeDocument from "./SummarizeDocument";
import TopicSummary from "./TopicSummary";

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

  const scrollToTopicSummary = () => {
    if (topicSummaryRef.current) {
      const yOffset = -80;
      const y =
        topicSummaryRef.current.getBoundingClientRect().top +
        window.scrollY +
        yOffset;
      window.scrollTo({ top: y, behavior: "smooth" });
    }
  };

  return (
    <div className="bg-gray-100">
      {/* Pass scroll function to Hero */}
      <Hero
        scrollToSummarize={scrollToSummarize}
        scrollToTopicSummary={scrollToTopicSummary}
      />

      {/* Sections */}
      <div ref={summarizeRef} className="mt-20">
        <SummarizeDocument />
      </div>

      {/* Add ref to Topic Summary */}
      <div ref={topicSummaryRef} className="mt-20">
        <TopicSummary />
      </div>
    </div>
  );
};

export default Summarization;
