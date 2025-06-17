// .src/components/Header.jsx
import React, { useState } from "react";
import { Link } from "react-router-dom";

function Header() {
    const [user, setUser] = useState(null); // Replace with actual user state management
    const handleLoginClick = () => setUser({ username: "JohnDoe", email: "johndoe@example.com" }); // Simulate user login
    const handleLogout = () => {
        // Logic to handle logout
        setUser(null);
    };
  return (
    <header className="flex justify-between items-center px-8 py-4 bg-white shadow">
      <div className="flex items-center gap-8">
        <Link to="/" className="text-3xl font-bold text-primary">UpNest</Link>
        <nav className="flex gap-4">
          <Link to="/dashboard" className="hover:text-primary">Dashboard</Link>
          <Link to="/add-baby" className="hover:text-primary">Add Baby</Link>
          <Link to="/ai-chat" className="hover:text-primary">AI Chat</Link>
        </nav>
      </div>
      {user ? (
        <div className="flex items-center gap-4">
          <div className="bg-primary text-white rounded-full w-10 h-10 flex items-center justify-center font-bold text-lg">
            {user.username[0]?.toUpperCase()}
          </div>
          <button
            className="bg-gray-200 text-primary px-4 py-2 rounded hover:bg-gray-300 transition"
            onClick={handleLogout}
          >
            Logout
          </button>
        </div>
      ) : (
        <button
          className="bg-primary text-white px-4 py-2 rounded hover:bg-primary/90 transition"
          onClick={handleLoginClick}
        >
          Login
        </button>
      )}
    </header>
  );
}

export default Header;
