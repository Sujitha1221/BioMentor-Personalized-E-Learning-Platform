import React, { useState } from 'react';

const Contact = () => {
    const [activeIndex, setActiveIndex] = useState(null);

  const toggleAccordion = (index) => {
    setActiveIndex(activeIndex === index ? null : index);
  };

  const faqs = [
    {
      question: "Do you offer discounts for students?",
      answer:
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco.",
    },
    {
      question: "Do you offer special pricing for big teams?",
      answer:
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco.",
    },
    {
      question: "What is the past experience of your teachers?",
      answer:
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco.",
    },
    {
      question: "What is the course refund policy?",
      answer:
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco.",
    },
    {
      question: "Do you offer discounts for non-profits?",
      answer:
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco.",
    },
  ];
    
    
    return (
        <div className='mt-32'>
            <div className="flex justify-center items-center bg-gray-100">
                <div className="w-full max-w-6xl p-12 bg-white shadow-lg rounded-lg">
                    <div className="flex flex-wrap -mx-4">
                        <div className="w-full md:w-1/2 px-4 mb-8 md:mb-0">
                            <h2 className="text-2xl font-semibold mb-4">Keep In Touch With Us.</h2>
                            <p className="text-gray-600 mb-8">
                                Neque convallis a cras semper auctor. Libero id faucibus nisl tincidunt egetnvallis.
                            </p>
                            <div className="mb-4">
                                <div className="flex items-center mb-2">
                                    <svg className="w-6 h-6 primary-color mr-2" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zm-4 10a7 7 0 00-5.546-6.775A3 3 0 002 13v1a3 3 0 003 3h14a3 3 0 003-3v-1a3 3 0 00-4.454-2.775A7 7 0 0012 17z"></path></svg>
                                    <span>328 Queensberry Street, North Melbourne VIC 3051,</span>
                                </div>
                            </div>
                            <div className="mb-4">
                                <div className="flex items-center mb-2">
                                    <svg className="w-6 h-6 primary-color mr-2" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" d="M3 10v4m0 0v4m0-4h4m-4 0H1m6-6h.01M10 14l1.553-.774m5.91 2.274A7.975 7.975 0 0112 20a7.975 7.975 0 01-5.464-2.134l1.414-1.415A6 6 0 0012 18a6 6 0 003.464-10.95L14.25 8m2.5-2.5L18 4m-6.5-1.5L12 2m2 2l.414-.414M4 6a2 2 0 11-4 0 2 2 0 014 0zm14 0a2 2 0 11-4 0 2 2 0 014 0zm0 12a2 2 0 11-4 0 2 2 0 014 0zM6 18a2 2 0 11-4 0 2 2 0 014 0zm10-10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
                                    <span>+1 123 456 7890</span>
                                </div>
                            </div>
                            <div className="mb-4">
                                <div className="flex items-center mb-2">
                                    <svg className="w-6 h-6 primary-color mr-2" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" d="M16 12H8m8 4H8m8-8H8m12-2a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2h12a2 2 0 002-2V6z"></path></svg>
                                    <span>hi@educrat.com</span>
                                </div>
                            </div>
                        </div>
                        <div className="w-full md:w-1/2 px-4">
                            <h2 className="text-2xl font-semibold mb-4">Send a Message.</h2>
                            <p className="text-gray-600 mb-8">
                                Neque convallis a cras semper auctor. Libero id faucibus nisl tincidunt egetnvallis.
                            </p>
                            <form>
                                <div className="mb-4">
                                    <input
                                        className="w-full p-3 border border-gray-300 rounded-lg"
                                        type="text"
                                        placeholder="Name..."
                                        required
                                    />
                                </div>
                                <div className="mb-4">
                                    <input
                                        className="w-full p-3 border border-gray-300 rounded-lg"
                                        type="email"
                                        placeholder="Email..." 
                                        required
                                    />
                                </div>
                                <div className="mb-4">
                                    <textarea
                                        className="w-full p-3 border border-gray-300 rounded-lg"
                                        rows="4"
                                        placeholder="Message..." 
                                        required
                                    ></textarea>
                                </div>
                                <button
                                    type="submit"
                                    className="w-full p-3 button-join rounded-lg"
                                >
                                    Send Message
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
            <div className="flex justify-center items-center min-h-screen bg-gray-100">
                <div className="w-full max-w-6xl p-12 bg-white shadow-lg rounded-lg">
                    <h2 className="text-3xl font-semibold mb-4 text-center">Frequently Asked Questions.</h2>
                    <p className="text-center text-gray-600 mb-8">
                        Ut enim ad minim veniam, quis nostrud exercitation ullamco
                    </p>
                    <div className="space-y-4">
                        {faqs.map((faq, index) => (
                            <div key={index} className="border border-gray-200 rounded-lg">
                                <button
                                    onClick={() => toggleAccordion(index)}
                                    className="w-full p-4 text-left flex justify-between items-center focus:outline-none"
                                >
                                    <span className={activeIndex === index ? "text-lg font-medium primary-color" : "text-lg font-medium"}>{faq.question}</span>
                                    <span className={activeIndex === index ? "text-xl primary-color" : "text-xl"}>
                                        {activeIndex === index ? '-' : '+'}
                                    </span>
                                </button>
                                {activeIndex === index && (
                                    <div className="p-4 border-t border-gray-200">
                                        <p className="text-gray-700">{faq.answer}</p>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Contact;