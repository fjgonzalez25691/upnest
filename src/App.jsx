import { useEffect } from "react";
import { Routes, Route } from "react-router-dom";
import { useAuth } from "react-oidc-context";
import { cognitoConfig } from "./auth/cognitoConfig.js";

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
import TestApiConnection from "./services/TestApiConnection"; // For testing API connection

// Components
import Header from "./components/Header";
import Footer from "./components/Footer";

function App() {
  const auth = useAuth();

  const signOutRedirect = () => {
    const clientId = cognitoConfig.client_id;
    const logoutUri = cognitoConfig.post_logout_redirect_uri;
    const cognitoDomain = cognitoConfig.cognitoDomain;
    
    // Clear user data
    auth.removeUser();
    
    // Redirect to Cognito logout endpoint
    window.location.href = `${cognitoDomain}/logout?client_id=${clientId}&logout_uri=${encodeURIComponent(logoutUri)}`;
  };

  // Redirect if not authenticated and not loading
  useEffect(() => {
    if (!auth.isAuthenticated && !auth.isLoading) {
      auth.signinRedirect();
    }
  }, [auth.isAuthenticated, auth.isLoading, auth]);

  if (auth.isLoading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  if (auth.error) {
    return <div className="flex items-center justify-center min-h-screen">Error: {auth.error.message}</div>;
  }

  // Prevent rendering the app while redirecting
  if (!auth.isAuthenticated && !auth.isLoading) {
    return null;
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header user={auth.user} onLoginClick={auth.signinRedirect} onLogout={signOutRedirect} />
      <main className="flex-1 flex justify-center items-center bg-background ">
        <Routes>
          <Route path="/" element={<Landing auth={auth} />} />
          <Route path="/register" element={<Register />} />
          <Route path="/login" element={<Login />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/add-baby" element={<AddBaby />} />
          <Route path="/add-growth-data/:babyId" element={<AddGrowthData />} />
          <Route path="/baby/:babyId" element={<BabyProfile />} />
          <Route path="/growth-chart/:babyId" element={<GrowthChart />} />
          <Route path="/ai-chat" element={<AIChat />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/test-api" element={<TestApiConnection />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}

export default App;