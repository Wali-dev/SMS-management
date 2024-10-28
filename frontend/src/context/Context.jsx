import React, { useState, useContext } from "react";

const AuthContext = React.createContext()

export function AuthProvider(props) {
    const [authUser, setAuthUser] = useState(null)
    const [isLoggedIn, setIsLoggedIn] = useState(false)
    const [token, setToken] = useState(null)

    // Add login and logout functions to handle auth state
    const login = (userData, authToken) => {
        setAuthUser(userData);
        setToken(authToken);
        setIsLoggedIn(true);
    };

    const logout = () => {
        setAuthUser(null);
        setToken(null);
        setIsLoggedIn(false);
    };

    const value = {
        authUser,
        setAuthUser,
        isLoggedIn,
        setIsLoggedIn,
        token,
        setToken,
        login,
        logout
    }

    return (

        <AuthContext.Provider value={value}>{props.children} </AuthContext.Provider>
    )
}

export function useAuth() {
    return useContext(AuthContext)
}