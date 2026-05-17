import axios from 'axios';

const api = axios.create({
    // In Docker: nginx handles /api/ → no need for full URL
    // In local dev (npm start): falls back to localhost:8000
    baseURL: process.env.REACT_APP_API_URL || '/api',
    timeout: 10000,
});

export default api;