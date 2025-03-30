import React, { useEffect, useState } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import SetUp from "./pages/SetUp";
import Settings from "./pages/Settings";
import Sidebar from "./components/Sidebar";
import Notifications from "./pages/Notifications";
import { fetchSetup } from "./services/api";

const Layout = ({ patientData, children }) => {
  const location = useLocation();
  const showSidebar = location.pathname !== "/setup";
  return (
    <div className="flex h-screen bg-gray-100">
      {showSidebar && <Sidebar patientData={patientData} />}
      <div className="flex-1">{children}</div>
    </div>
  );
};

function App() {
  const [patientData, setPatientData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkSetup = async () => {
      try {
        const data = await fetchSetup();
        if (data && data.name) {
          setPatientData(data);
          localStorage.setItem("patientId", data._id);
        }
      } catch (error) {
        console.error("Error fetching setup:", error);
      } finally {
        setLoading(false);
      }
    };
    checkSetup();
  }, []);

  if (loading) return <p className="text-center text-xl">Loading...</p>;

  const isSetupComplete = !!(patientData && patientData.name);

  return (
    <Router>
      <Layout patientData={patientData}>
        <Routes>
          <Route path="/" element={isSetupComplete ? <Dashboard patientData={patientData} /> : <Navigate to="/setup" />} />
          <Route path="/setup" element={isSetupComplete ? <Navigate to="/dashboard" /> : <SetUp />} />
          <Route path="/dashboard" element={isSetupComplete ? <Dashboard patientData={patientData} /> : <Navigate to="/setup" />} />
          <Route path="/notifications" element={isSetupComplete ? <Notifications /> : <Navigate to="/setup" />} />
          <Route path="/settings" element={isSetupComplete ? <Settings patientData={patientData} /> : <Navigate to="/setup" />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
