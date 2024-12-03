import React, { useState } from "react";
import vocabulary from '../data/vocabulary.json';
import Flashcard from "./FlashCard";

const FlashcardDeck = () => {
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [showNextCard, setShowNextCard] = useState(false);

  const handleFlashcardSubmitted = () => {
    setShowNextCard(true);
  };

  return (
    <div className="flex justify-center items-center h-screen">
      <Flashcard
        term={vocabulary[currentCardIndex].term}
        hint={vocabulary[currentCardIndex].hint}
        onFlashcardSubmitted={handleFlashcardSubmitted}
      />
    </div>
  );
};

export default FlashcardDeck;
