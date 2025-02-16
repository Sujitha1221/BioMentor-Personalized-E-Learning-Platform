import React from 'react';
import Cisco from '../../assets/logo/cisco.svg';
import Amazon from '../../assets/logo/amazon.svg';
import AMD from '../../assets/logo/amd.svg';
import DropCam from '../../assets/logo/dropcam.svg';
import Logitech from '../../assets/logo/logitech.svg';
import Spotify from '../../assets/logo/spotify.svg';

const TrustedBrand = () => {
    return (
        <div className='w-4/5 mx-auto'>
            <h5 className='text-center text-lg mb-8'>Trusted by the world’s best</h5>
            <div className='flex flex-wrap justify-center gap-10'>
                <img className='w-24 h-auto' src={Cisco} alt="Cisco" />
                <img className='w-24 h-auto' src={Amazon} alt="Amazon" />
                <img className='w-24 h-auto' src={AMD} alt="AMD" />
                <img className='w-24 h-auto' src={DropCam} alt="DropCam" />
                <img className='w-24 h-auto' src={Logitech} alt="Logitech" />
                <img className='w-24 h-auto' src={Spotify} alt="Spotify" />
            </div>
        </div>
    );
};

export default TrustedBrand;
