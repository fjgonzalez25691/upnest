import axios from "axios";

// Create a base axios instance for all API requests
const axiosClient = axios.create({
  baseURL: "https://ukm4je3juj.execute-api.eu-south-2.amazonaws.com",
  headers: {
    "Content-Type": "application/json",
  },
});

// Attach Cognito token (if available) before each request
axiosClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("cognito_token"); // Replace with secure storage as needed
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default axiosClient;
