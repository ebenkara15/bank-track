import { useAuth } from "@clerk/clerk-react";
import axios from "axios";

const API_URL = process.env.API_URL | "http://localhost:8000";

const { getToken } = useAuth();

const apiClient = axios.create({
    baseURL: API_URL,
    timeout: 1000,
    headers: { 'Authorization': `Bearer ${await getToken()}` }
});
