import React, { useRef } from "react";
import Hero from "./Hero";
import VocabularyMastery from "./VocabularyMastery";
import CompeteAndLearn from "./CompeteAndLearn";
import ViewProgress from "./ViewProgress";

const VocabularyMemorization = () => {
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
        <VocabularyMastery />
      </div>

      {/* Add ref to Topic Summary */}
      <div ref={topicSummaryRef} className="mt-10">
        <CompeteAndLearn />
      </div>

      <div ref={topicSummaryRef} className="mt-10">
        <ViewProgress />
      </div>
    </div>
  );
};

export default VocabularyMemorization;
