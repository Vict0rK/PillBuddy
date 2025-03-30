// import React, { useState, useEffect } from "react";

// const dummyNotifications = [
//   {
//     id: 1,
//     title: "Medication Reminder",
//     message: "Time to take your 500mg medication.",
//     time: "10:00 AM",
//   },
//   {
//     id: 2,
//     title: "Missed Dose Alert",
//     message: "You missed your dose at 8:00 AM.",
//     time: "8:05 AM",
//   },
//   {
//     id: 3,
//     title: "Unauthorized Access",
//     message: "An unauthorized access attempt was detected.",
//     time: "9:30 AM",
//   },
//   {
//     id: 4,
//     title: "Refill Reminder",
//     message: "Your medication stock is low. Please refill soon.",
//     time: "Yesterday",
//   }
// ];

// const Notifications = () => {
//   const [notifications, setNotifications] = useState([]);

//   useEffect(() => {
//     // Set dummy notifications on mount
//     setNotifications(dummyNotifications);
//   }, []);

//   const clearNotifications = () => {
//     setNotifications([]);
//   };

//   return (
//     <div className="min-h-screen bg-gray-100 p-6">
//       <div className="flex justify-between items-center mb-6">
//         <h2 className="text-2xl font-bold">Notifications</h2>
//         <button
//           onClick={clearNotifications}
//           className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
//         >
//           Clear Notifications
//         </button>
//       </div>
//       <div className="space-y-4">
//         {notifications.length === 0 ? (
//           <p className="text-gray-600 m-10">No notifications available.</p>
//         ) : (
//           notifications.map((notif) => (
//             <div
//               key={notif.id}
//               className="bg-white rounded-xl shadow p-4 flex items-center transition-transform transform hover:scale-105"
//             >
//               <div className="flex-1">
//                 <h3 className="text-lg font-semibold text-gray-800">
//                   {notif.title}
//                 </h3>
//                 <p className="text-gray-600">{notif.message}</p>
//               </div>
//               <div className="text-right">
//                 <span className="text-sm text-gray-500">{notif.time}</span>
//               </div>
//             </div>
//           ))
//         )}
//       </div>
//     </div>
//   );
// };

// export default Notifications;

import React, { useEffect, useState } from "react";
import { fetchNotifications, clearNotifications } from "../services/api";

const Notifications = () => {
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    const loadNotifications = async () => {
      try {
        const data = await fetchNotifications();
        setNotifications(data);
      } catch (err) {
        console.error("Failed to fetch notifications:", err);
      }
    };
    loadNotifications();
  }, []);

  const handleClearNotifications = async () => {
    try {
      await clearNotifications();
      setNotifications([]);
    } catch (err) {
      console.error("Failed to clear notifications:", err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Notifications</h2>
        <button
          onClick={handleClearNotifications}
          className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
        >
          Clear Notifications
        </button>
      </div>
      <div className="space-y-4">
        {notifications.length === 0 ? (
          <p className="text-gray-600 m-10">No notifications available.</p>
        ) : (
          notifications.map((notif, index) => (
            <div
              key={index}
              className="bg-white rounded-xl shadow p-4 flex items-center transition-transform transform hover:scale-105"
            >
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-800">
                  {notif.title || notif.user}
                </h3>
                <p className="text-gray-600">{notif.message || notif.action}</p>
              </div>
              <div className="text-right">
                <span className="text-sm text-gray-500">
                  {new Date(notif.time).toLocaleString()}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Notifications;