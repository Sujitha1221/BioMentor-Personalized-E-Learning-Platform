import React from 'react';
import Hero from './Hero';
import SummarizeDocument from './SummarizeDocument';

const Summarization = () => {
    return (
        <div>
            <div> {/* Adjusted margin for different screen sizes */}
                <Hero />
                <SummarizeDocument/>
            </div>
        </div>
    );
};

export default Summarization;
