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
];

const ModalLoadingScreen = () => {
  const [factIndex, setFactIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setFactIndex((prevIndex) => (prevIndex + 1) % biologyFacts.length);
    }, 6000); // Change fact every 6 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div
      className="fixed inset-0 flex justify-center items-center bg-gray-800 bg-opacity-90 z-50"
      style={{ pointerEvents: "auto" }} // Ensures clicks do not dismiss loading
      onClick={(e) => e.stopPropagation()} // Prevents clicks from closing the modal
    >
      <div
        className="flex flex-col justify-center items-center"
        style={{ pointerEvents: "auto" }}
      >
        {/* Rotating 3D Molecular Model */}
        <motion.div
          className="relative w-24 h-24 border-4 border-[#6440FB] rounded-full shadow-2xl"
          animate={{ rotate: [0, 360] }}
          transition={{ repeat: Infinity, duration: 4, ease: "linear" }}
        >
          {/* Atoms within the molecule */}
          {[...Array(6)].map((_, i) => {
            const randomTop = Math.random() * 80 + "%";
            const randomLeft = Math.random() * 80 + "%";

            return (
              <motion.div
                key={i}
                className="absolute w-4 h-4 bg-[#140342] rounded-full shadow-lg"
                style={{
                  top: randomTop,
                  left: randomLeft,
                }}
                animate={{
                  scale: [1, 1.3, 1],
                  opacity: [1, 0.5, 1],
                }}
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

        {/* Pulsating Molecular Energy Effect */}
        <motion.div
          className="absolute w-40 h-40 bg-[#6440FB] bg-opacity-60 rounded-full"
          animate={{
            scale: [1, 1.6, 1],
            opacity: [0.5, 0.2, 0.5],
          }}
          transition={{ repeat: Infinity, duration: 3, ease: "easeInOut" }}
        />

        {/* Loading Text */}
        <p className="mt-6 text-white text-lg font-semibold tracking-wide z-50">
          Processing, please wait...
        </p>

        {/* Rotating Biology Facts */}
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

export default ModalLoadingScreen;
