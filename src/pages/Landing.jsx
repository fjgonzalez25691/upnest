// Description: Landing page component for UpNest application
// src/pages/Landing.jsx

import React from "react";
import PrimaryButton from "../components/PrimaryButton";

// This is a simple landing page component
// that can be expanded with more features later.

const Landing = () => {
  return (
    <div className="flex flex-col items-center justify-center h-full w-full ">
      <h1 className="text-2xl font-bold mb-4">Welcome to UpNest</h1>
      <p className="mb-4">Your one-stop solution for all your needs.</p>
      <div className="flex space-x-4">
        <PrimaryButton>Login</PrimaryButton>
        <PrimaryButton>Register</PrimaryButton>
      </div>
    </div>
  );
};

export default Landing;

