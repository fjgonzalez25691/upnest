// .src/components/InputField.jsx
// Purpose: A reusable input field component for the UpNest application. Used for forms and user input.

import React from "react";
import { Link } from "react-router-dom";

const Navbar = () => (
  <nav className="bg-surface shadow-md p-4 flex justify-between items-center">
    <Link to="/" className="text-primary font-bold text-xl">UpNest</Link>
    <div className="flex gap-4">
      <Link to="/dashboard" className="text-textmain hover:text-primary">Dashboard</Link>
      <Link to="/settings" className="text-textmain hover:text-primary">Settings</Link>
      <Link to="/login" className="text-danger hover:text-primary">Logout</Link>
    </div>
  </nav>
);

export default Navbar;
// This Navbar component provides a simple navigation bar with links to the dashboard, settings, and logout.