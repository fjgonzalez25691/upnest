// src/hooks/useCurrentUser.js
import { useAuth } from "react-oidc-context";

/**
 * Custom hook to get current user information
 * Returns user data including the sub (user ID) for database operations
 */
export const useCurrentUser = () => {
  const auth = useAuth();

  const getCurrentUserId = () => {
    return auth.user?.profile?.sub || null;
  };

  const getCurrentUserEmail = () => {
    return auth.user?.profile?.email || null;
  };

  const getCurrentUserName = () => {
    return auth.user?.profile?.name || auth.user?.profile?.email || null;
  };

  const isAuthenticated = auth.isAuthenticated;
  const isLoading = auth.isLoading;

  return {
    userId: getCurrentUserId(),
    email: getCurrentUserEmail(),
    name: getCurrentUserName(),
    isAuthenticated,
    isLoading,
    user: auth.user,
    // Helper methods
    getCurrentUserId,
    getCurrentUserEmail,
    getCurrentUserName
  };
};
