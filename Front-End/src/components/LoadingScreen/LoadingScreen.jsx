import { motion } from "framer-motion";
import { FaDna, FaMicroscope, FaLeaf, FaFlask } from "react-icons/fa";
import { useState, useEffect } from "react";

const facts = [
  "The human genome contains approximately 3 billion base pairs.",
  "Your body produces about 25 million new cells every second.",
  "DNA molecules are coiled so tightly that if unwrapped, they could stretch to the sun and back over 600 times.",
  "The average human carries about 2kg of bacteria in their body.",
  "There are more bacterial cells in your body than human cells!"
];

const icons = [FaDna, FaDna];

const LoadingScreen = () => {
  const [factIndex, setFactIndex] = useState(0);
  const [iconIndex, setIconIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setFactIndex((prevIndex) => (prevIndex + 1) % facts.length);
      setIconIndex((prevIndex) => (prevIndex + 1) % icons.length);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  const IconComponent = icons[iconIndex];

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-white text-indigo-950 p-8">
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
        className="relative flex items-center justify-center w-28 h-28 rounded-full shadow-2xl bg-gradient-to-r from-indigo-500 to-indigo-900 border-4 border-indigo-950 border-t-transparent"
      >
        <div className="absolute flex items-center justify-center w-full h-full">
          <IconComponent className="text-white text-6xl" />
        </div>
      </motion.div>
      <p className="mt-8 text-3xl font-extrabold tracking-wider text-indigo-950 drop-shadow-lg">Processing Biological Insights...</p>
      <motion.p
        key={factIndex}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        transition={{ duration: 0.5 }}
        className="text-lg text-indigo-700 mt-4 text-center italic max-w-lg px-4"
      >
        {facts[factIndex]}
      </motion.p>
      <motion.div
        animate={{ opacity: [0, 1, 0] }}
        transition={{ repeat: Infinity, duration: 3, ease: "easeInOut" }}
        className="mt-6 text-sm text-green-600 bg-green-100 px-4 py-2 rounded-lg shadow-md"
      >
        Tip: Keep exploring the mysteries of biology with curiosity and passion!
      </motion.div>
    </div>
  );
};

export default LoadingScreen;