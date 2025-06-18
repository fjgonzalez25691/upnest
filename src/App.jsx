import React, {useState} from "react";
import { Routes, Route } from "react-router-dom";

// Pages
import Landing from "./pages/Landing";
import Register from "./pages/Register";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import AddBaby from "./pages/AddBaby";
import AddGrowthData from "./pages/AddGrowthData";
import BabyProfile from "./pages/BabyProfile";
import GrowthChart from "./pages/GrowthChart";
import AIChat from "./pages/AIChat";
import Settings from "./pages/Settings";

// Components
import Header from "./components/Header";
import Footer from "./components/Footer";

function App() {
  const [user, setUser] = useState(null); // Simulated user state
  const handleLoginClick = () => setUser({ username: "JohnDoe", email: "johndoe@example.com" });
  const handleLogout = () => {
    // Logic to handle logout
    setUser(null);
  };
  return (
    
      <div className="min-h-screen flex flex-col">
        <Header user={user} onLoginClick={handleLoginClick} onLogout={handleLogout} />
        <main className="flex-1 flex justify-center items-center bg-background ">

          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/register" element={<Register />} />
            <Route path="/login" element={<Login />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/add-baby" element={<AddBaby />} />
            <Route path="/add-growth-data/:babyId" element={<AddGrowthData />} />
            <Route path="/baby/:babyId" element={<BabyProfile />} />
            <Route path="/growth-chart/:babyId" element={<GrowthChart />} />
            <Route path="/ai-chat" element={<AIChat />} />
            <Route path="/settings" element={<Settings />} />
            {/* Add more routes as needed */}
          </Routes>
        </main>
        <Footer />
      </div>
    
  );
}

export default App;

