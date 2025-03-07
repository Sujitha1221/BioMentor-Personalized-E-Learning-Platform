import React from 'react';
import errorImage from "../../assets/image/maintain.jpg"

const UnderDevelopment = () => {
    return (
        <div className='w-4/5 mx-auto'>
            <img className='sm:w-4/5 lg:w-1/2 mx-auto' src={errorImage} alt="" />
        </div>
    );
};

export default UnderDevelopment;