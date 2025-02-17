import React from 'react';

const PromoSection = () => {
    return (
        <div className=" flex justify-center items-center ">
            <div className="w-3/4 mx-auto px-4 py-12 flex flex-col-reverse md:flex-row items-center justify-between">
                <div className="md:w-1/2">
                    <h2 className="text-4xl font-bold mb-4">
                        <span className="text-purple-600">Learn</span> new <span className='text-color font-bold'>Skills</span> when and where you like.
                    </h2>
                    <p className="text-gray-600 mb-6">
                        Use the list below to bring attention to your product's key differentiator.
                    </p>
                    <ul className="mb-6 space-y-2">
                        <li className="flex items-center">
                            <svg className="w-6 h-6 text-purple-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>
                            Hand-picked authors
                        </li>
                        <li className="flex items-center">
                            <svg className="w-6 h-6 text-purple-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>
                            Easy to follow curriculum
                        </li>
                        <li className="flex items-center">
                            <svg className="w-6 h-6 text-purple-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>
                            Free courses
                        </li>
                        <li className="flex items-center">
                            <svg className="w-6 h-6 text-purple-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>
                            Money-back guarantee
                        </li>
                    </ul>
                    <button className="button-join text-white py-2 px-10 rounded-lg w-full sm:w-auto  focus:outline-none">
                        Join Free
                    </button>
                </div>
                <div className=" mt-8 md:mt-0 md:ml-8">
                    <img
                        src="https://educrat-nextjs.vercel.app/_next/image?url=%2Fassets%2Fimg%2Fabout%2F1.png&w=750&q=75"
                        alt="Promo"
                        className="w-full max-w-md rounded-lg"
                    />
                </div>
            </div>
        </div>
    );
};

export default PromoSection;