import React, { useEffect } from 'react';
import { useAuth } from 'react-oidc-context';
import { useNavigate } from 'react-router-dom';
import Loader from '../components/Loader';
import PrimaryButton from '../components/PrimaryButton';

const AuthCallback = () => {
  const auth = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (auth.isAuthenticated) {
      // Check if there's a stored redirect path
      const redirectPath = sessionStorage.getItem('redirectAfterLogin');
      
      if (redirectPath) {
        // Clear the stored path
        sessionStorage.removeItem('redirectAfterLogin');
        // Navigate to the originally requested path
        navigate(redirectPath);
      } else {
        // Default to dashboard if no redirect path
        navigate('/dashboard');
      }
    }
  }, [auth.isAuthenticated, navigate]);

  if (auth.error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="bg-surface p-8 rounded-2xl shadow-md text-center max-w-md mx-4">
          <h2 className="text-xl font-bold mb-4 text-red-500">Authentication Error</h2>
          <p className="mb-6 text-textsubtle">{auth.error.message}</p>
          <PrimaryButton
            onClick={() => navigate('/')}
          >
            Return to Home
          </PrimaryButton>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="bg-surface p-8 rounded-2xl shadow-md text-center max-w-md mx-4">
        <div className="mb-4">
          <Loader />
        </div>
        <h2 className="text-xl font-bold mb-2 text-primary">Processing Authentication</h2>
        <p className="text-textsubtle">Please wait while we complete your login...</p>
      </div>
    </div>
  );
};

export default AuthCallback;
