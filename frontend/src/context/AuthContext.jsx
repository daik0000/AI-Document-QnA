import { createContext, useContext, useState, useEffect } from 'react';
import client from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) { // If no token is found, set loading to false and return early
            setLoading(false);
            return;
        }
        client
        .get('/auth/me') // Make a request to the /auth/me endpoint to validate the token and get user data
        .then((res) => setUser(res.data)) // If the token is valid, set the user data
        .catch(() => localStorage.removeItem('token')) // If the token is invalid, remove it from localStorage
        .finally(() => setLoading(false)); // Set loading to false after the request is completed, regardless of success or failure
    }, []);

    const login = async (email, password) => {
        const form = new URLSearchParams();
        form.append('username', email);
        form.append('password', password);

        const res = await client.post('/auth/login', form, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        });
        localStorage.setItem('token', res.data.access_token);

        const me = await client.get('/auth/me');
        setUser(me.data);
    };

    const register = async (email, password, fullName) => {
        await client.post('/auth/register', {
            email,
            password,
            full_name: fullName,
        });
    };

    const logout = () => {
        localStorage.removeItem('token');
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, register, logout }}>
        {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    return useContext(AuthContext);
}
