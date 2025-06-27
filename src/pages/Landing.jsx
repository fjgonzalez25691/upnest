// Landing page component for UpNest application
// src/pages/Landing.jsx
// Main entry point showing app features and authentication options

import React from "react";
import { useAuth } from "react-oidc-context";
import { Link } from "react-router-dom";
import PrimaryButton from "../components/PrimaryButton";

const Landing = () => {
  const auth = useAuth();

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center px-6">
      <div className="max-w-2xl mx-auto text-center">
        <h1 className="text-4xl md:text-6xl font-bold text-primary mb-6">
          Welcome to UpNest
        </h1>
        <p className="text-lg md:text-xl text-textsubtle mb-8">
          Track your baby's growth, milestones, and development with our comprehensive monitoring tools.
        </p>
        
        {auth.isAuthenticated ? (
          <div className="space-y-4">
            <p className="text-primary font-medium">
              Welcome back, {auth.user?.profile?.name || auth.user?.profile?.email}!
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/dashboard">
                <PrimaryButton className="w-full sm:w-auto">
                  Go to Dashboard
                </PrimaryButton>
              </Link>
              <Link to="/add-baby">
                <button className="w-full sm:w-auto bg-secondary text-white px-6 py-2 rounded-lg font-semibold hover:bg-secondary/90 transition-colors">
                  Add Baby
                </button>
              </Link>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            <p className="text-gray-600">
              Please log in to start tracking your baby's development journey.
            </p>
            <PrimaryButton 
              onClick={() => auth.signinRedirect()}
              className="text-lg px-8 py-3"
            >
              Get Started
            </PrimaryButton>
          </div>
        )}

        {/* Features Preview */}
        <div className="mt-16 grid md:grid-cols-3 gap-8">
          <div className="bg-surface p-6 rounded-2xl shadow-md">
            <h3 className="text-xl font-bold text-primary mb-3">Growth Tracking</h3>
            <p className="text-textsubtle">Monitor weight, height, and development milestones over time.</p>
          </div>
          <div className="bg-surface p-6 rounded-2xl shadow-md">
            <h3 className="text-xl font-bold text-primary mb-3">AI Insights</h3>
            <p className="text-textsubtle">Get personalized recommendations and answers to your questions.</p>
          </div>
          <div className="bg-surface p-6 rounded-2xl shadow-md">
            <h3 className="text-xl font-bold text-primary mb-3">Progress Charts</h3>
            <p className="text-textsubtle">Visualize your baby's growth with beautiful charts and graphs.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Landing;

