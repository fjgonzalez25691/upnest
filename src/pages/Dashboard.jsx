// src/pages/Dashboard.jsx
// Dashboard component displaying user information and babies list
import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useCurrentUser } from "../hooks/useCurrentUser";
import { getBabies } from "../services/babyApi";
import PrimaryButton from "../components/PrimaryButton";

const Dashboard = () => {
  const { user, userId, email, name } = useCurrentUser();
  const [babies, setBabies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Fetch user's babies on component mount
  useEffect(() => {
    const fetchBabies = async () => {
      try {
        setLoading(true);
        const babiesData = await getBabies();
        setBabies(babiesData);
      } catch (err) {
        console.error("Error fetching babies:", err);
        setError("Failed to load babies. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    if (userId) {
      fetchBabies();
    }
  }, [userId]);

  // The ProtectedRoute component handles authentication redirect
  // So we can assume user is authenticated here
  
  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-primary mb-8">My Dashboard</h1>
        
        {/* Welcome message */}
        <div className="bg-primary/10 border border-primary/20 rounded-2xl p-6 mb-6">
          <h2 className="text-xl font-semibold text-primary mb-2">
            Welcome back, {name || 'Parent'}! 👋
          </h2>
          <p className="text-gray-600">
            Here you can manage your babies' growth data and track their development.
          </p>
        </div>

        {/* My Babies Section */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-primary">My Babies</h2>
            <Link to="/add-baby">
              <PrimaryButton>Add New Baby</PrimaryButton>
            </Link>
          </div>

          {loading ? (
            <div className="bg-surface p-6 rounded-2xl shadow-md text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
              <p className="text-gray-600">Loading babies...</p>
            </div>
          ) : error ? (
            <div className="bg-red-50 border border-red-200 rounded-2xl p-6">
              <p className="text-red-600">{error}</p>
            </div>
          ) : babies.length === 0 ? (
            <div className="bg-surface p-6 rounded-2xl shadow-md text-center">
              <p className="text-gray-600 mb-4">You haven't added any babies yet.</p>
              <Link to="/add-baby">
                <PrimaryButton>Add Your First Baby</PrimaryButton>
              </Link>
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {babies.map((baby) => (
                <div key={baby.id} className="bg-surface p-6 rounded-2xl shadow-md hover:shadow-lg transition-shadow">
                  <h3 className="text-xl font-semibold text-primary mb-2">{baby.name}</h3>
                  <p className="text-gray-600 mb-1">
                    <strong>Born:</strong> {new Date(baby.dob).toLocaleDateString()}
                  </p>
                  <p className="text-gray-600 mb-1">
                    <strong>Sex:</strong> {baby.sex}
                  </p>
                  {baby.premature && (
                    <p className="text-gray-600 mb-1">
                      <strong>Premature:</strong> {baby.gestationalWeek} weeks
                    </p>
                  )}
                  
                  <div className="flex gap-2 mt-4">
                    <Link to={`/baby/${baby.id}`} className="flex-1">
                      <button className="w-full bg-primary text-white px-3 py-2 rounded text-sm hover:bg-primary/90">
                        View Profile
                      </button>
                    </Link>
                    <Link to={`/add-growth-data/${baby.id}`} className="flex-1">
                      <button className="w-full bg-green-500 text-white px-3 py-2 rounded text-sm hover:bg-green-600">
                        Add Data
                      </button>
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        
        <div className="grid gap-6 md:grid-cols-2">
          {/* User Info Card */}
          <div className="bg-surface p-6 rounded-2xl shadow-md">
            <h2 className="text-xl font-bold mb-4 text-primary">User Information</h2>
            <div className="space-y-3">
              <div>
                <span className="font-medium text-gray-700">Name:</span>
                <span className="ml-2 text-gray-900">{name || 'Not provided'}</span>
              </div>
              <div>
                <span className="font-medium text-gray-700">Email:</span>
                <span className="ml-2 text-gray-900">{email || 'Not provided'}</span>
              </div>
              <div>
                <span className="font-medium text-gray-700">User ID:</span>
                <span className="ml-2 text-gray-900 text-sm break-all">{userId || 'Not provided'}</span>
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
