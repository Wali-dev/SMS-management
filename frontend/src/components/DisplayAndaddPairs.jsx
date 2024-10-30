import { useState, useEffect } from 'react';
import { CiCirclePlus } from "react-icons/ci";
import Table from "./Table";

const DisplayAndaddPairs = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [isAnimating, setIsAnimating] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [formData, setFormData] = useState({
        pairName: '',
        proxy: '',
        numberList: null
    });
    const [error, setError] = useState('');

    useEffect(() => {
        if (isOpen) {
            setIsAnimating(true);
        } else {
            const timer = setTimeout(() => {
                setIsAnimating(false);
                // Reset form data when popup closes
                setFormData({
                    pairName: '',
                    proxy: '',
                    numberList: null
                });
                setError('');
            }, 300);
            return () => clearTimeout(timer);
        }
    }, [isOpen]);

    const handleClose = () => {
        setIsOpen(false);
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        setFormData(prev => ({
            ...prev,
            numberList: file
        }));
    };

    const handleSubmit = async () => {
        try {
            setIsLoading(true);
            setError('');

            const formDataToSend = new FormData();
            formDataToSend.append('pair_name', formData.pairName);
            formDataToSend.append('proxy', formData.proxy);
            if (formData.numberList) {
                formDataToSend.append('number_list', formData.numberList);
            }

            const response = await fetch('http://127.0.0.1:5000/program/create', {
                method: 'POST',
                headers: {
                    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjcxZTQ4MTYzMmRkNjUwOGZiMGViOTkxIiwiZXhwIjoxNzMwMzE2NDQxfQ.F5Xd0_EQKpsv-qBVdilS_KL9HS5D0CryRKp0WZeg_c0'
                },
                body: formDataToSend
            });

            if (!response.ok) {
                throw new Error('Failed to create country pair');
            }

            const data = await response.json();
            console.log('Success:', data);
            handleClose();
        } catch (err) {
            setError(err.message);
            console.error('Error:', err);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        const handleEscape = (e) => {
            if (e.key === 'Escape') {
                handleClose();
            }
        };

        if (isOpen) {
            document.addEventListener('keydown', handleEscape);
        }

        return () => {
            document.removeEventListener('keydown', handleEscape);
        };
    }, [isOpen]);

    return (
        <div className="m-2">
            <div className="flex justify-center items-center space-x-2">
                <button
                    onClick={() => setIsOpen(true)}
                    className="flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition duration-200 ease-in-out shadow-lg"
                >
                    <CiCirclePlus className="text-2xl mr-2" />
                    <span className="font-medium">Add Country Pair</span>
                </button>
            </div>

            {isAnimating && (
                <div
                    className={`fixed inset-0 bg-black transition-opacity duration-300 ease-in-out ${isOpen ? 'bg-opacity-50' : 'bg-opacity-0'
                        }`}
                    onClick={handleClose}
                />
            )}

            {isAnimating && (
                <div className="fixed inset-0 flex items-center justify-center z-50 pointer-events-none">
                    <div
                        className={`bg-white rounded-lg shadow-xl w-full max-w-md mx-4 pointer-events-auto
                            transform transition-all duration-300 ease-in-out
                            ${isOpen ? 'translate-y-0 opacity-100' : 'translate-y-8 opacity-0'}`}
                        onClick={e => e.stopPropagation()}
                    >
                        <div className="flex items-center justify-between p-4 border-b">
                            <h2 className="text-xl font-semibold text-gray-800">Add New Country Pair</h2>
                            <button
                                onClick={handleClose}
                                className="p-2 hover:bg-gray-100 rounded-full transition-colors duration-200"
                            >
                                <svg
                                    className="w-4 h-4 text-gray-600"
                                    fill="none"
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth="2"
                                    viewBox="0 0 24 24"
                                    stroke="currentColor"
                                >
                                    <path d="M6 18L18 6M6 6l12 12"></path>
                                </svg>
                            </button>
                        </div>

                        <div className="p-6 space-y-4">
                            {error && (
                                <div className="bg-red-50 text-red-500 p-3 rounded-md text-sm">
                                    {error}
                                </div>
                            )}

                            <div className="space-y-2">
                                <label className="block text-sm font-medium text-gray-700">
                                    Pair Name
                                </label>
                                <input
                                    type="text"
                                    name="pairName"
                                    value={formData.pairName}
                                    onChange={handleInputChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                                    placeholder="Enter pair name"
                                />
                            </div>

                            <div className="space-y-2">
                                <label className="block text-sm font-medium text-gray-700">
                                    Proxy
                                </label>
                                <input
                                    type="text"
                                    name="proxy"
                                    value={formData.proxy}
                                    onChange={handleInputChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                                    placeholder="Enter proxy"
                                />
                            </div>

                            <div className="space-y-2">
                                <label className="block text-sm font-medium text-gray-700">
                                    Number List
                                </label>
                                <input
                                    type="file"
                                    onChange={handleFileChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                                    accept=".txt,.csv"
                                />
                            </div>

                            <button
                                onClick={handleSubmit}
                                disabled={isLoading}
                                className={`w-full px-4 py-2 text-white rounded-md transition duration-200 ease-in-out ${isLoading
                                    ? 'bg-green-400 cursor-not-allowed'
                                    : 'bg-green-600 hover:bg-green-700'
                                    }`}
                            >
                                {isLoading ? 'Saving...' : 'Save Country Pair'}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            <div>
                <Table trigger={isOpen} />
            </div>
        </div>
    );
};

export default DisplayAndaddPairs;