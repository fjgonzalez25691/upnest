// src/pages/Dashboard.jsx
// Dashboard component displaying user information and token details for development
import React from "react";
import { useAuth } from "react-oidc-context";
import { Navigate } from "react-router-dom";

const Dashboard = () => {
  const auth = useAuth();

  // Redirect to landing page if user is not authenticated
  if (!auth.isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const user = auth.user;

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-primary mb-8">Dashboard</h1>
        
        <div className="grid gap-6 md:grid-cols-2">
          {/* User Info Card */}
          <div className="bg-surface p-6 rounded-2xl shadow-md">
            <h2 className="text-xl font-bold mb-4 text-primary">User Information</h2>
            <div className="space-y-3">
              <div>
                <span className="font-medium text-gray-700">Name:</span>
                <span className="ml-2 text-gray-900">{user?.profile?.name || 'Not provided'}</span>
              </div>
              <div>
                <span className="font-medium text-gray-700">Email:</span>
                <span className="ml-2 text-gray-900">{user?.profile?.email || 'Not provided'}</span>
              </div>
              <div>
                <span className="font-medium text-gray-700">User ID:</span>
                <span className="ml-2 text-gray-900 text-sm break-all">{user?.profile?.sub || 'Not provided'}</span>
              </div>
              <div>
                <span className="font-medium text-gray-700">Email Verified:</span>
                <span className="ml-2 text-gray-900">{user?.profile?.email_verified ? 'Yes' : 'No'}</span>
              </div>
            </div>
          </div>

          {/* Token Info Card */}
          <div className="bg-surface p-6 rounded-2xl shadow-md">
            <h2 className="text-xl font-bold mb-4 text-primary">Token Information</h2>
            <div className="space-y-3">
              <div>
                <span className="font-medium text-gray-700">Token Type:</span>
                <span className="ml-2 text-gray-900">{user?.token_type || 'Bearer'}</span>
              </div>
              <div>
                <span className="font-medium text-gray-700">Expires At:</span>
                <span className="ml-2 text-gray-900">
                  {user?.expires_at ? new Date(user.expires_at * 1000).toLocaleString() : 'Not available'}
                </span>
              </div>
              <div>
                <span className="font-medium text-gray-700">Scope:</span>
                <span className="ml-2 text-gray-900">{user?.scope || 'Not provided'}</span>
              </div>
              <div>
                <span className="font-medium text-gray-700">Session State:</span>
                <span className="ml-2 text-gray-900 text-sm break-all">{user?.session_state || 'Not provided'}</span>
              </div>
            </div>
          </div>

          {/* Access Token Preview */}
          <div className="bg-surface p-6 rounded-2xl shadow-md md:col-span-2">
            <h2 className="text-xl font-bold mb-4 text-primary">Access Token (Preview)</h2>
            <div className="bg-gray-100 p-4 rounded-lg overflow-hidden">
              <p className="text-sm text-gray-600 mb-2">Token (first 100 characters):</p>
              <code className="text-xs text-gray-800 break-all">
                {user?.access_token ? `${user.access_token.substring(0, 100)}...` : 'Not available'}
              </code>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Full token available in browser storage for API calls
            </p>
          </div>

          {/* Quick Actions */}
          <div className="bg-surface p-6 rounded-2xl shadow-md md:col-span-2">
            <h2 className="text-xl font-bold mb-4 text-primary">Quick Actions</h2>
            <div className="flex flex-wrap gap-4">
              <button className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary/90 transition-colors">
                Add Baby
              </button>
              <button className="bg-secondary text-white px-4 py-2 rounded-lg hover:bg-secondary/90 transition-colors">
                View Growth Chart
              </button>
              <button className="bg-accent text-white px-4 py-2 rounded-lg hover:bg-accent/90 transition-colors">
                AI Chat
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
