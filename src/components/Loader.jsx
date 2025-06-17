// .src/components/InputField.jsx
// Purpose: A reusable input field component for the UpNest application. Used for forms and user input.

import React from "react";

const Loader = () => (
  <div className="flex items-center justify-center p-8">
    <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
  </div>
);

export default Loader;
// This Loader component provides a simple loading spinner that can be used throughout the application to indicate loading states.