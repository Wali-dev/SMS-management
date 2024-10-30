import { useState } from "react";
import { useAuth } from "../context/Context";

const Navbar = () => {
    const { authUser } = useAuth();
    const [isLoading, setIsLoading] = useState(false);

    const handleLogout = async () => {
        setIsLoading(true); // Start loading animation
        try {
            // Add logout functionality here, e.g., await logout();
        } finally {
            setIsLoading(false); // Stop loading animation
        }
    };

    return (
        <nav className="flex justify-between items-center p-4 bg-gray-800 shadow-lg">
            <div className="text-white text-lg">Hello, {authUser}</div>
            <button
                onClick={handleLogout}
                className={`px-4 py-2 flex items-center justify-center text-white bg-red-500 hover:bg-red-600 rounded transition-colors duration-200 ease-in-out ${isLoading && "cursor-not-allowed"}`}
                disabled={isLoading} // Disable button while loading
            >
                {isLoading ? (
                    <svg
                        className="animate-spin h-5 w-5 mr-2 text-white"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                    >
                        <circle
                            className="opacity-25"
                            cx="12"
                            cy="12"
                            r="10"
                            stroke="currentColor"
                            strokeWidth="4"
                        ></circle>
                        <path
                            className="opacity-75"
                            fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                        ></path>
                    </svg>
                ) : (
                    "Logout"
                )}
            </button>
        </nav>
    );
};

export default Navbar;
