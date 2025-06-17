// .src/components/PrimaryButton.jsx
// Pourpose: A reusable primary button component for the UpNest application. Used for primary actions like submitting forms or confirming actions.

import React from "react";

const PrimaryButton = ({ children, onClick, type = "button", className = "" }) => (
  <button
    type={type}
    onClick={onClick}
    className={`bg-primary text-white rounded-lg px-6 py-2 font-semibold shadow hover:bg-primary/90 transition-colors ${className}`}
  >
    {children}
  </button>
);

export default PrimaryButton;
