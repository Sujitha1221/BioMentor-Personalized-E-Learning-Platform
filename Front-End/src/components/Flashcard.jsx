import React, { useState } from "react";

const Flashcard = ({ term, hint, onFlashcardSubmitted }) => {
  const [flipped, setFlipped] = useState(false); // Local flipped state for each flashcard
  const [userInput, setUserInput] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    setFlipped(true); // Flip the card to show the term
    onFlashcardSubmitted(); // Notify the parent to show the next card after 3 seconds
  };

  return (
    <div className="relative w-80 h-48 perspective-1000">
      {/* Flashcard Container with Flip Effect */}
      <div
        className={`w-full h-full transition-transform duration-700 transform-style-preserve-3d ${
          flipped ? "rotate-y-180" : ""
        }`}
      >
        {/* Front Side - Initially showing the hint */}
        <div
          className={`absolute w-full h-full bg-white shadow-[0_0_10px_0_rgba(0,0,0,0.5)] rounded-lg p-4 flex flex-col justify-center items-center backface-hidden`}
        >
          <p className="text-gray-600 text-lg mb-4 text-center">{hint}</p>
          <form onSubmit={handleSubmit} className="flex flex-col gap-2 w-full">
            <input
              type="text"
              placeholder="Your answer..."
              className="border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 w-full"
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
            />
            <button
              type="submit"
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 w-full"
            >
              Submit
            </button>
          </form>
        </div>

        {/* Back Side - Will show the term after flipping */}
        <div
          className={`absolute w-full h-full bg-blue-500 text-white shadow-lg rounded-lg p-4 flex justify-center items-center rotate-y-180 backface-hidden`}
        >
          <p className="text-2xl font-semibold">{term}</p>
        </div>
      </div>
    </div>
  );
};

export default Flashcard;
