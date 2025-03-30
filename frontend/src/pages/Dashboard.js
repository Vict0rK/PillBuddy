import React from "react";
import TopStats from "../components/dashboard/TopStats";
import Analytics from "../components/dashboard/Analytics";
import Inventory from "../components/dashboard/Inventory";
import Logs from "../components/dashboard/Logs";

const Dashboard = ({ patientData }) => {
  return (
    <div className="flex flex-col p-6 overflow-y-auto h-full">
      <TopStats />
      <Analytics />
      <div className="flex gap-6 mt-6">
        <Inventory patientId={patientData ? patientData._id : ""} />
        <Logs />
      </div>
    </div>
  );
};

export default Dashboard;
