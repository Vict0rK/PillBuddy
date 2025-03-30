import React, { useState } from "react";
import { Link } from "react-router-dom";
import logo from "../assets/images/logo.png";
import { FaChartBar, FaCog, FaChevronDown, FaChevronUp, FaBell } from "react-icons/fa";

const Sidebar = ({ patientData }) => {
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const toggleDropdown = () => {
    setDropdownOpen((prev) => !prev);
  };

  return (
    <div className="w-1/6 bg-gray-900 text-white h-screen flex flex-col py-6">
      {/* Logo */}
      <div className="flex justify-start mb-8 px-4">
        <img src={logo} alt="TimeCapsule Logo" className="w-48 h-auto" />
      </div>

      {/* Patient Name Display*/}
      {patientData && (
        <div className="mb-6 px-4">
          <button
            onClick={toggleDropdown}
            className="w-full flex justify-between items-center bg-gray-800 p-3 rounded-lg shadow focus:outline-none"
          >
            <span className="text-lg text-gray-300">{patientData.name}</span>
            {dropdownOpen ? (
              <FaChevronUp className="text-gray-300" />
            ) : (
              <FaChevronDown className="text-gray-300" />
            )}
          </button>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 px-4">
        <ul className="space-y-4">
          <li>
            <Link to="/dashboard" className="flex items-center space-x-2 hover:text-gray-400">
              <FaChartBar className="text-xl" />
              <span className="text-lg">Dashboard</span>
            </Link>
          </li>
          <li>
            <Link to="/notifications" className="flex items-center space-x-2 hover:text-gray-400">
              <FaBell className="text-xl" />
              <span className="text-lg">Notifications</span>
            </Link>
          </li>
          <li>
            <Link to="/settings" className="flex items-center space-x-2 hover:text-gray-400">
              <FaCog className="text-xl" />
              <span className="text-lg">Settings</span>
            </Link>
          </li>
        </ul>
      </nav>
    </div>
  );
};

export default Sidebar;
