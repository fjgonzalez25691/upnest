import React, {useState} from "react";
import { Routes, Route } from "react-router-dom";

import Landing from "./pages/Landing";
import Register from "./pages/Register";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import AddBaby from "./pages/AddBaby";
import BabyProfile from "./pages/BabyProfile";
import GrowthChart from "./pages/GrowthChart";
import AIChat from "./pages/AIChat";
import Settings from "./pages/Settings";
import Header from "./components/Header";

function App() {
  const [user, setUser] = useState(null); // Simulated user state
  const handleLoginClick = () => setUser({ username: "JohnDoe", email: "johndoe@example.com" });
  const handleLogout = () => {
    // Logic to handle logout
    setUser(null);
  };
  return (
    <>
      <Header user={user} onLoginClick={handleLoginClick} onLogout={handleLogout} />
      
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/register" element={<Register />} />
          <Route path="/login" element={<Login />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/add-baby" element={<AddBaby />} />
          <Route path="/baby/:babyId" element={<BabyProfile />} />
          <Route path="/growth-chart/:babyId" element={<GrowthChart />} />
          <Route path="/ai-chat" element={<AIChat />} />
          <Route path="/settings" element={<Settings />} />
          {/* Puedes añadir rutas para 404/not found aquí si quieres */}
        </Routes>
    </>
  );
}

export default App;

