import axios from 'axios';

// This is the base URL for our Django API.
// axios will prepend this to every request.
const api = axios.create({
    baseURL: 'http://localhost:8000/api',
    timeout: 10000,  // Give up after 10 seconds
});

export default api;