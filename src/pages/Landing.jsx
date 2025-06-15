// Description: Landing page component for UpNest application
// src/pages/Landing.jsx

import React from "react";

// This is a simple landing page component
// that can be expanded with more features later.

const Landing = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h1 className="text-2xl font-bold mb-4">Welcome to UpNest</h1>
      <p className="mb-4">Your one-stop solution for all your needs.</p>
      <div className="flex space-x-4">
        <button className="btn">Login</button>
        <button className="btn">Register</button>
      </div>
    </div>
  );
};

export default Landing;
// Note: The "btn" class is assumed to be defined in your CSS for styling buttons.
// You can replace it with your own styles or a UI library class.
