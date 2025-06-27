import axios from "axios";

// Create a base axios instance for all API requests
const axiosClient = axios.create({
  baseURL: "https://ukm4je3juj.execute-api.eu-south-2.amazonaws.com",
  headers: {
    "Content-Type": "application/json",
  },
});

// Function to set the auth object for token access
let authContext = null;

export const setAuthContext = (auth) => {
  authContext = auth;
};

// Attach Cognito token (if available) before each request
axiosClient.interceptors.request.use(
  async (config) => {
    try {
      // Try to get token from react-oidc-context first
      if (authContext && authContext.user && authContext.user.access_token) {
        config.headers.Authorization = `Bearer ${authContext.user.access_token}`;
      } else {
        // Fallback to localStorage (for backward compatibility)
        const token = localStorage.getItem("cognito_token");
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      }
    } catch (error) {
      console.warn("Failed to attach auth token:", error);
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle 401 errors
axiosClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      console.warn("Unauthorized request, token may be expired");
      
      // Try to refresh token if using react-oidc-context
      if (authContext && authContext.signinSilent) {
        try {
          await authContext.signinSilent();
          // Retry the original request with new token
          const originalRequest = error.config;
          if (authContext.user && authContext.user.access_token) {
            originalRequest.headers.Authorization = `Bearer ${authContext.user.access_token}`;
            return axiosClient(originalRequest);
          }
        } catch (refreshError) {
          console.error("Token refresh failed:", refreshError);
          // Redirect to login if refresh fails
          if (authContext.signinRedirect) {
            authContext.signinRedirect();
          }
        }
      }
    }
    return Promise.reject(error);
  }
);

export default axiosClient;
