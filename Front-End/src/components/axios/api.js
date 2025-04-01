import axios from "axios";
import { MCQ_URL} from "../util/config"
// Base URL of your FastAPI backend
const api = axios.create({
  baseURL: MCQ_URL, 
});

// Attach access token to all requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Auto-refresh token when access token expires
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response && error.response.status === 401) {
      try {
        // Retrieve refresh token from localStorage
        const refreshToken = localStorage.getItem("refresh_token");
        if (!refreshToken) {
          throw new Error("No refresh token found. Logging out...");
        }

        // Call the /refresh endpoint with refresh token in request body
        const refreshResponse = await axios.post(
          `http://127.0.0.1:8001/refresh`,
          { refresh_token: refreshToken } // Send refresh token in body
        );

        const newToken = refreshResponse.data.access_token;

        // Store the new access token in localStorage
        localStorage.setItem("token", newToken);

        // Retry the failed request with the new token
        error.config.headers.Authorization = `Bearer ${newToken}`;
        return axios(error.config);
      } catch (refreshError) {
        console.error("Refresh token expired or invalid. Logging out...");
        localStorage.removeItem("token");
        localStorage.removeItem("refresh_token"); // Clear refresh token too
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default api;
