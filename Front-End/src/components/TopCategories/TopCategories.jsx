import React from 'react';
import icon1 from '../../assets/icons/1.svg';
import icon2 from '../../assets/icons/2.svg';
import icon3 from '../../assets/icons/3.svg';
import icon4 from '../../assets/icons/4.svg';
import icon5 from '../../assets/icons/5.svg';
import icon6 from '../../assets/icons/6.svg';
import './TopCategories.css';
import { Link } from 'react-router-dom';

const TopCategories = () => {
    return (
        <div className="w-2/3 mx-auto mt-20">
            <div className="text-center">
                <h1 className="text-4xl font-bold mt-5">Top Categories</h1>
                <p className="text-gray-400 mt-5">Lorem ipsum dolor sit amet, consectetur.</p>
            </div>
            <div className="flex flex-wrap justify-center gap-8 mt-20">
                <Link className="category w-full sm:w-1/2 lg:w-1/6 bg-slate-200 py-5 px-3 rounded-lg" to="/">
                    <div className="flex justify-center flex-col">
                        <div className="bg-white p-4 rounded-full mx-auto mt-5">
                            <img src={icon1} alt="" />
                        </div>
                        <p className="text-center text-xl mt-5">Design <br />Creative</p>
                        <p className="text-center text-gray-500 text-sm mt-5">537+ Courses</p>
                    </div>
                </Link>
                <Link className="category w-full sm:w-1/2 lg:w-1/6 bg-slate-200 py-5 px-3 rounded-lg" to="/">
                    <div className="flex justify-center flex-col">
                        <div className="bg-white p-4 rounded-full mx-auto mt-5">
                            <img src={icon2} alt="" />
                        </div>
                        <p className="text-center text-xl mt-5">Sales Marketing</p>
                        <p className="text-center text-gray-500 text-sm mt-5">540+ Courses</p>
                    </div>
                </Link>
                <Link className="category w-full sm:w-1/2 lg:w-1/6 bg-slate-200 py-5 px-3 rounded-lg" to="/">
                    <div className="flex justify-center flex-col">
                        <div className="bg-white p-4 rounded-full mx-auto mt-5">
                            <img src={icon3} alt="" />
                        </div>
                        <p className="text-center text-xl mt-5 mx-auto">Development IT</p>
                        <p className="text-center text-gray-500 text-sm mt-5">125+ Courses</p>
                    </div>
                </Link>
                <Link className="category w-full sm:w-1/2 lg:w-1/6 bg-slate-200 py-5 px-3 rounded-lg" to="/">
                    <div className="flex justify-center flex-col">
                        <div className="bg-white p-4 rounded-full mx-auto mt-5">
                            <img src={icon4} alt="" />
                        </div>
                        <p className="text-center text-xl mt-5">Engineering Architecture</p>
                        <p className="text-center text-gray-500 text-sm mt-5">37+ Courses</p>
                    </div>
                </Link>
                <Link className="category w-full sm:w-1/2 lg:w-1/6 bg-slate-200 py-5 px-3 rounded-lg" to="/">
                    <div className="flex justify-center flex-col">
                        <div className="bg-white p-4 rounded-full mx-auto mt-5">
                            <img src={icon5} alt="" />
                        </div>
                        <p className="text-center text-xl mt-5">Personal Development</p>
                        <p className="text-center text-gray-500 text-sm mt-5">980+ Courses</p>
                    </div>
                </Link>
                <Link className="category w-full sm:w-1/2 lg:w-1/6 bg-slate-200 py-5 px-3 rounded-lg" to="/">
                    <div className="flex justify-center flex-col">
                        <div className="bg-white p-4 rounded-full mx-auto mt-5">
                            <img src={icon6} alt="" />
                        </div>
                        <p className="text-center text-xl mt-5">Finance Accounting</p>
                        <p className="text-center text-gray-500 text-sm mt-5">228+ Courses</p>
                    </div>
                </Link>
            </div>
        </div>
    );
};

export default TopCategories;
