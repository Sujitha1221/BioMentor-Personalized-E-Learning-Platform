import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";

const biologyFacts = [
  "💡 Did you know? Your body has more bacteria than human cells!",
  "🧬 DNA molecules in a single cell can stretch over 6 feet if uncoiled!",
  "🩸 Red blood cells travel 12,000 miles in your body every day!",
  "🌱 Plants convert sunlight into energy in just milliseconds!",
  "🧠 Your brain generates enough electricity to power a small light bulb!",
  "🦠 The human body carries about 39 trillion microbial cells!",
  "👀 Your eyes can distinguish about 10 million different colors!",
  "💖 The human heart beats about 100,000 times a day!",
  "🦴 Bones are about 5 times stronger than steel of the same density!",
  "🫀 The aorta is nearly the diameter of a garden hose!",
  "🔬 A single teaspoon of soil contains more microorganisms than people on Earth!",
  "🦑 Octopuses have three hearts and blue blood!",
  "💨 Your lungs contain about 300 million alveoli, giving them a surface area the size of a tennis court!",
  "🔥 Your body produces about 25 million new cells every second!",
  "🦋 Butterflies can taste with their feet!",
  "🐙 An octopus can change its color in less than a second!",
  "🐦 The smallest bird, the bee hummingbird, weighs less than a penny!",
  "💧 The human body is about 60% water!",
  "🌿 Bamboo is the fastest-growing plant, growing up to 35 inches per day!",
  "🦷 Your enamel is the hardest substance in the human body!",
  "🧠 Your brain has about 86 billion neurons!",
  "💤 A jellyfish has no brain, heart, or bones, yet it can survive for millions of years!",
  "🦎 Some lizards can regrow their tails after losing them!",
  "🦠 There are more bacterial cells in your mouth than people on Earth!",
  "🕷️ The silk from a spider’s web is stronger than steel of the same thickness!",
  "🥚 The ostrich lays the largest eggs of any living land animal!",
  "🔋 Your body produces about 100 watts of power at rest!",
  "🦅 Eagles have eyesight up to 8 times sharper than humans!",
  "🐋 The blue whale is the largest animal ever to have lived on Earth!",
  "🧪 Your stomach acid is strong enough to dissolve stainless steel!",
];

const QuizLoadingScreen = () => {
  const [fact, setFact] = useState("");

  useEffect(() => {
    // Pick a random biology fact on each render
    const randomFact =
      biologyFacts[Math.floor(Math.random() * biologyFacts.length)];
    setFact(randomFact);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-blue-300 to-green-200 text-gray-900 p-6">
      <motion.div
        className="text-center bg-white p-6 rounded-xl shadow-xl"
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex items-center justify-center">
          <div className="w-12 h-12 border-4 border-blue-500 border-dotted rounded-full animate-spin"></div>
        </div>
        <h2 className="text-2xl font-bold mt-4">Loading...</h2>
        <p className="text-lg text-gray-700 mt-2 italic">"{fact}"</p>
      </motion.div>
    </div>
  );
};

export default QuizLoadingScreen;
