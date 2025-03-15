import { useState, useEffect } from "react";
import { motion } from "framer-motion";

const biologyFacts = [
  "Your body has around 37.2 trillion cells, each performing specialized functions.",
  "Mitochondria have their own DNA, inherited only from your mother.",
  "DNA uncoiled from one human cell can stretch about 2 meters in length!",
  "The human brain contains around 86 billion neurons, forming trillions of connections.",
  "There are more bacterial cells in your body than human cells.",
  "Photosynthesis produces over 90% of the Earth's oxygen supply.",
  "Viruses are not technically living organisms as they cannot reproduce without a host.",
  "CRISPR technology allows scientists to edit genes with extreme precision.",
  "Your heart beats around 100,000 times per day, pumping nearly 7,500 liters of blood.",
  "The largest single-celled organism is Caulerpa taxifolia, a giant algae spanning meters.",
  "The human genome contains approximately 3 billion base pairs of DNA.",
  "Some species of jellyfish are biologically immortal, meaning they can revert to earlier stages of life.",
  "The average human sheds about 600,000 skin particles every hour.",
  "Octopuses have three hearts and blue blood due to copper-rich hemocyanin.",
  "Bananas share about 60% of their DNA with humans!",
  "The axolotl can regenerate entire limbs, spinal cord, and even parts of its heart and brain.",
  "Tardigrades (water bears) can survive extreme radiation, boiling heat, and freezing cold.",
  "Your bones are about five times stronger than steel of the same density.",
  "The longest-living cells in your body are brain cells, which can last an entire lifetime.",
  "A single drop of seawater may contain millions of microscopic organisms, including bacteria and plankton.",
  "Elephants have the largest brain of any land animal, weighing about 5 kg (11 lbs).",
  "The smell of freshly-cut grass is actually a plant distress signal!",
  "A hummingbird's heart beats over 1,200 times per minute during flight.",
  "Sharks have been around for over 400 million years, making them older than dinosaurs!",
  "Butterflies can taste with their feet!",
];

const loadingMessages = [
  "🔄 Generating your quiz, please hold on...",
  "📡 Fetching the best questions for you...",
  "⏳ Calibrating difficulty levels for your quiz...",
  "🚀 Almost there! Preparing your personalized quiz...",
  "🎯 Making sure every question is engaging and challenging...",
  "📊 Analyzing your previous attempts for a better experience...",
  "🔬 Science takes time! Crafting your quiz carefully...",
  "🎉 Just a moment! Your quiz is getting ready...",
  "✅ Done! Your quiz is ready, loading now...",
];

const LoadingScreen = ({ quizReady }) => {
  const [factIndex, setFactIndex] = useState(
    Math.floor(Math.random() * biologyFacts.length)
  );
  const [loadingMessageIndex, setLoadingMessageIndex] = useState(
    Math.floor(Math.random() * loadingMessages.length)
  );

  useEffect(() => {
    const interval = setInterval(() => {
      setFactIndex(Math.floor(Math.random() * biologyFacts.length));
      setLoadingMessageIndex(
        Math.floor(Math.random() * loadingMessages.length)
      );
    }, 6000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div
      className="fixed inset-0 flex justify-center items-center bg-gray-800 bg-opacity-90 z-50"
      style={{ pointerEvents: "auto" }}
      onClick={(e) => e.stopPropagation()}
    >
      <div
        className="flex flex-col justify-center items-center"
        style={{ pointerEvents: "auto" }}
      >
        <motion.div
          className="relative w-24 h-24 border-4 border-[#6440FB] rounded-full shadow-2xl"
          animate={{ rotate: [0, 360] }}
          transition={{ repeat: Infinity, duration: 4, ease: "linear" }}
        >
          {[...Array(6)].map((_, i) => {
            const randomTop = Math.random() * 80 + "%";
            const randomLeft = Math.random() * 80 + "%";
            return (
              <motion.div
                key={i}
                className="absolute w-4 h-4 bg-[#140342] rounded-full shadow-lg"
                style={{ top: randomTop, left: randomLeft }}
                animate={{ scale: [1, 1.3, 1], opacity: [1, 0.5, 1] }}
                transition={{
                  repeat: Infinity,
                  duration: 2,
                  delay: i * 0.3,
                  ease: "easeInOut",
                }}
              />
            );
          })}
        </motion.div>

        <motion.div
          className="absolute w-40 h-40 bg-[#6440FB] bg-opacity-60 rounded-full"
          animate={{ scale: [1, 1.6, 1], opacity: [0.5, 0.2, 0.5] }}
          transition={{ repeat: Infinity, duration: 3, ease: "easeInOut" }}
        />

        <p className="mt-6 text-white text-lg font-semibold tracking-wide z-50">
          {quizReady
            ? "✅ Your quiz is ready! Loading now..."
            : loadingMessages[loadingMessageIndex]}
        </p>

        <motion.p
          className="mt-4 text-white text-center max-w-xs sm:max-w-md md:max-w-lg lg:max-w-xl xl:max-w-2xl px-4 sm:px-6 md:px-8 text-xs sm:text-sm md:text-base lg:text-lg font-medium z-50"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.5 }}
        >
          🔬 {biologyFacts[factIndex]}
        </motion.p>
      </div>
    </div>
  );
};

export default LoadingScreen;
