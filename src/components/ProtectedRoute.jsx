// src/components/ProtectedRoute.jsx
import React, { useState, useEffect } from "react";
import { useAuth } from "react-oidc-context";
import { useLocation } from "react-router-dom";
import Modal from "./Modal";
import PrimaryButton from "./PrimaryButton";

const ProtectedRoute = ({ children }) => {
  const auth = useAuth();
  const location = useLocation();
  const [showLoginModal, setShowLoginModal] = useState(false);

  // Store the attempted route for redirect after login
  useEffect(() => {
    if (!auth.isAuthenticated && !auth.isLoading) {
      // Store current path in sessionStorage for redirect after login
      sessionStorage.setItem('redirectAfterLogin', location.pathname + location.search);
    }
  }, [auth.isAuthenticated, auth.isLoading, location]);

  // Show loading state while auth is initializing
  if (auth.isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // If authenticated, render the protected content
  if (auth.isAuthenticated) {
    return children;
  }

  // If not authenticated, show login modal automatically
  if (!showLoginModal) {
    setShowLoginModal(true);
  }

  const handleLogin = () => {
    auth.signinRedirect();
  };

  const handleCloseModal = () => {
    setShowLoginModal(false);
    // Clear the redirect path since user chose not to login
    sessionStorage.removeItem('redirectAfterLogin');
    // Redirect to home page when modal is closed
    window.location.href = '/';
  };

  return (
    <>
      {/* Show a placeholder while modal is handled */}
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">
            Authentication Required
          </h2>
          <p className="text-gray-600 mb-6">
            Please login to access this feature
          </p>
          <PrimaryButton onClick={handleLogin}>
            Login Now
          </PrimaryButton>
        </div>
      </div>

      {/* Login Modal */}
      <Modal 
        isOpen={showLoginModal} 
        onClose={handleCloseModal}
        title="Login Required"
      >
        <div className="text-center py-4">
          <div className="mb-6">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-yellow-100 mb-4">
              <svg className="h-6 w-6 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 19.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Authentication Required
            </h3>
            <p className="text-sm text-gray-500 mb-6">
              You need to be logged in to access this feature. Please login to continue or return to the home page.
            </p>
          </div>
          
          <div className="flex gap-3 justify-center">
            <button
              onClick={handleCloseModal}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
            >
              Back to Home
            </button>
            <PrimaryButton onClick={handleLogin}>
              Login
            </PrimaryButton>
          </div>
        </div>
      </Modal>
    </>
  );
};

export default ProtectedRoute;
