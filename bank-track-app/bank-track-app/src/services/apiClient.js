import { useAuth } from "@clerk/clerk-react";
import axios from "axios";

const apiClient = axios.create({
    baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
    timeout: 10000, // You can set a timeout for all requests
    headers: {
        'Content-Type': 'application/json',
        'Authorization': '',
    },
});

const { getToken } = useAuth();

apiClient.defaults.headers.common['Authorization'] = `Bearer ${await getToken()}`;

// Optional: Set up interceptors for common logic like auth tokens, logging, etc.
apiClient.interceptors.request.use(
    config => {
        // Add authorization header or any global request changes
        const token = localStorage.getItem('token'); // Example: Get token from local storage
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    error => {
        return Promise.reject(error);
    }
);

apiClient.interceptors.response.use(
    response => response,
    error => {
        // Handle global errors (like 401 for unauthorized)
        if (error.response.status === 401) {
            // Handle unauthorized access
        }
        return Promise.reject(error);
    }
);

export default apiClient;
