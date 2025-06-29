import { useEffect } from "react";
import { Routes, Route } from "react-router-dom";
import { useAuth } from "react-oidc-context";
import { setAuthContext } from "./services/axiosClient";

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
import AuthCallback from "./pages/AuthCallback";
import TestApiConnection from "./services/TestApiConnection"; // For testing API connection

// Components
import Header from "./components/Header";
import Footer from "./components/Footer";
import ProtectedRoute from "./components/ProtectedRoute";

function App() {
  const auth = useAuth();

  // Redirect handling for authentication flow
  useEffect(() => {
    // Configure axios with auth context
    setAuthContext(auth);
    
    // No automatic redirect - let users navigate freely
    // Only redirect to dashboard after successful login
    if (auth.isAuthenticated && window.location.pathname === '/callback') {
      // This is handled in AuthCallback component
    }
  }, [auth.isAuthenticated, auth.isLoading, auth]);

  if (auth.isLoading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  if (auth.error) {
    return <div className="flex items-center justify-center min-h-screen">Error: {auth.error.message}</div>;
  }

  // Don't prevent rendering - let users navigate freely
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 bg-background">
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/callback" element={<AuthCallback />} />
          <Route path="/register" element={<Register />} />
          <Route path="/login" element={<Login />} />
          <Route path="/ai-chat" element={<AIChat />} />
          <Route path="/test-api" element={<TestApiConnection />} />
          
          {/* Protected Routes */}
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          <Route path="/add-baby" element={
            <ProtectedRoute>
              <AddBaby />
            </ProtectedRoute>
          } />
          <Route path="/add-growth-data/:babyId" element={
            <ProtectedRoute>
              <AddGrowthData />
            </ProtectedRoute>
          } />
          <Route path="/baby/:babyId" element={
            <ProtectedRoute>
              <BabyProfile />
            </ProtectedRoute>
          } />
          <Route path="/growth-chart/:babyId" element={
            <ProtectedRoute>
              <GrowthChart />
            </ProtectedRoute>
          } />
          <Route path="/settings" element={
            <ProtectedRoute>
              <Settings />
            </ProtectedRoute>
          } />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}

export default App;