import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { FaExclamationTriangle } from "react-icons/fa";
import mqtt from "mqtt"; // Import the mqtt library
import { addLog, fetchLogs as fetchLogsFromAPI } from "../../services/api"; // Rename fetchLogs to fetchLogsFromAPI

// Logs Component: Displays logs and MQTT messages
const Logs = () => {
  const [logs, setLogs] = useState([]);
  const [modalContent, setModalContent] = useState(null);
  const [mqttMessage, setMqttMessage] = useState(""); // State to store the MQTT message

  const handleImageClick = (image) => {
    setModalContent({
      title: "Unauthorized Access Detected",
      image: image,
    });
  };

  // Fetch logs from the API and set them to the state
  const loadLogs = async () => {
    try {
      const data = await fetchLogsFromAPI(); // Call the imported fetchLogs function
      setLogs(data.reverse()); // Set logs fetched from the backend
    } catch (error) {
      console.error("Error fetching logs:", error);
    }
  };

  // Effect to fetch logs and set up MQTT client when the component mounts
  useEffect(() => {
    loadLogs(); // Fetch logs when the component mounts

    const topics = [
      "pillbuddy/wrong_medication_alert",
      "pillbuddy/correct_medication_alert",
      "pillbuddy/wrong_dosage_alert",
      "pillbuddy/image"
    ];

    const client = mqtt.connect("ws://192.168.220.172:9001"); // Your MQTT broker URL

    client.on("connect", () => {
      console.log("Connected to MQTT broker");

      // Subscribe to multiple topics
      client.subscribe(topics, (err) => {
        if (err) {
          console.error("Error subscribing to topics:", err);
        } else {
          console.log(`Subscribed to topics: ${topics.join(", ")}`);
        }
      });
    });

    console.log("Before receive message");

    client.on("message", async (topic, rawMessage) => {
      let payloadString = rawMessage.toString();
      let parsedPayload;
    
      try {
        // Attempt to parse the incoming payload as JSON
        parsedPayload = JSON.parse(payloadString);
      } catch (error) {
        // If parsing fails, we’ll treat the entire payload as a simple string (for normal string logs)
        parsedPayload = { message: payloadString };
      }
    
      // Extract fields from the parsed payload
      const { message, image } = parsedPayload;
    
      // Log the text part of the message
      console.log(`Received message on topic ${topic}: ${message || payloadString}`);
    
      // Build the log data
      const logData = {
        user: "Patient",
        action: `${message || payloadString}`,
        time: new Date().toISOString(),
        ...(image && { image: `data:image/jpeg;base64,${image}`}), // add image field if an image exists
      };
    
      try {
        // If there's an image, handle it
        // if (image) {
        //   // Example: Display or store the base64 image
        //   console.log("Received image base64:", image);
        // }
    
        // Call API to add log to DB
        await addLog(logData);
    
        // Update logs in state
        setLogs((prevLogs) => [ logData, ...prevLogs]);
    
      } catch (error) {
        // Handle errors
        console.error("Error adding log or handling image:", error);
      }
    });
    

    client.on("error", (err) => {
      console.error("MQTT Error:", err);
    });

    return () => {
      if (client) {
        topics.forEach((topic) => client.unsubscribe(topic));
        client.end();
      }
    };
  }, []); // Empty dependency array to run this effect only once when the component mounts

   return (
    <div className="bg-white p-6 rounded-lg shadow-md flex flex-col w-full">
      <h3 className="text-lg font-semibold mb-4">Logs</h3>

      {/* Display MQTT message */}
      {mqttMessage && (
        <div className="bg-yellow-100 text-yellow-800 p-4 mb-4 rounded-lg">
          <h4 className="font-semibold">MQTT Message:</h4>
          <p>{mqttMessage}</p>
        </div>
      )}

      <div className="overflow-x-auto w-full max-h-64 overflow-y-auto">
        <table className="min-w-full table-auto">
          <thead className="bg-gray-100 sticky top-0">
            <tr>
              <th className="px-4 py-2 text-left">User</th>
              <th className="px-4 py-2 text-left">Action</th>
              <th className="px-4 py-2 text-left">Time</th>
            </tr>
          </thead>
          <tbody>
            {logs.length === 0 ? (
              <tr>
                <td colSpan="3" className="text-center py-4">
                  No logs available
                </td>
              </tr>
            ) : (
              logs.map((log, index) => (
                <tr key={index} className="border-b">
                  <td className="px-4 py-2">{log.user}</td>
                  <td className="px-4 py-2 flex items-center">
                    {log.action}
                    {log.action.toLowerCase().includes("unauthorized") &&
                      log.image && (
                        <button
                          onClick={() => handleImageClick(log.image)}
                          className="ml-2 text-red-500 hover:text-red-700"
                        >
                          <FaExclamationTriangle />
                        </button>
                      )}
                  </td>
                  <td className="px-4 py-2">
                    {new Date(log.time).toLocaleString()}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Modal for showing unauthorized access image */}
      {modalContent && (
        <motion.div
          className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <motion.div
            className="bg-white p-6 rounded-lg shadow-lg text-center"
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
          >
            <h2 className="text-lg font-semibold mb-4">{modalContent.title}</h2>
            <img
              src={modalContent.image}
              alt="Unauthorized Access"
              className="max-w-full max-h-96 mx-auto"
            />
            <button
              className="bg-blue-500 text-white px-4 py-2 rounded mt-4 hover:bg-blue-600"
              onClick={() => setModalContent(null)}
            >
              Close
            </button>
          </motion.div>
        </motion.div>
      )}
    </div>
  );
};

export default Logs;
