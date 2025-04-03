import React, { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { FaExclamationTriangle } from "react-icons/fa";
import mqtt from "mqtt";
import { addLog, fetchLogs as fetchLogsFromAPI } from "../../services/api";

const Logs = () => {
  const [logs, setLogs] = useState([]);
  const [modalContent, setModalContent] = useState(null);
  const [mqttMessage, setMqttMessage] = useState("");
  const clientRef = useRef(null);

  const handleImageClick = (image) => {
    setModalContent({
      title: "Unauthorized Access Detected",
      image: image,
    });
  };

  // Fetch logs from the API and set them in state
  const loadLogs = async () => {
    try {
      const data = await fetchLogsFromAPI();
      setLogs(data.reverse());
    } catch (error) {
      console.error("Error fetching logs:", error);
    }
  };

  useEffect(() => {
    loadLogs();
  }, []);

  // Set up persistent MQTT subscriptions for log topics
  useEffect(() => {
    const topics = [
      "pillbuddy/wrong_medication_alert",
      "pillbuddy/correct_medication_alert",
      "pillbuddy/wrong_dosage_alert",
      "pillbuddy/image",
    ];
    
    if (!clientRef.current) {
      clientRef.current = mqtt.connect("ws://192.168.220.172:9001", {
        clientId: "logs_client_" + Math.random().toString(16).substr(2, 8),
        keepalive: 30,
        reconnectPeriod: 1000,
      });
    }
    const client = clientRef.current;

    client.on("connect", () => {
      console.log("Connected to MQTT broker for Logs");
      client.subscribe(topics, (err) => {
        if (err) {
          console.error("Error subscribing to topics:", err);
        } else {
          console.log(`Subscribed to topics: ${topics.join(", ")}`);
        }
      });
    });

    client.on("message", async (topic, rawMessage) => {
      let payloadString = rawMessage.toString();
      let parsedPayload;
    
      try {
        parsedPayload = JSON.parse(payloadString);
      } catch (error) {
        parsedPayload = { message: payloadString };
      }
    
      const { message, image } = parsedPayload;
      console.log(`Received message on topic ${topic}: ${message || payloadString}`);
    
      const logData = {
        user: "Patient",
        action: `${message || payloadString}`,
        time: new Date().toISOString(),
        ...(image && { image: `data:image/jpeg;base64,${image}` }),
      };
    
      try {
        await addLog(logData);
        setLogs((prevLogs) => [logData, ...prevLogs]);
      } catch (error) {
        console.error("Error adding log or handling image:", error);
      }
    });

    client.on("error", (err) => {
      console.error("MQTT Error in Logs:", err);
    });

    // Cleanup: Unsubscribe from topics on unmount
    return () => {
      topics.forEach((topic) =>
        client.unsubscribe(topic, (err) => {
          if (err) console.error("Error unsubscribing", err);
        })
      );
    };
  }, []);

  return (
    <div className="bg-white p-6 rounded-lg shadow-md flex flex-col w-full">
      <h3 className="text-lg font-semibold mb-4">Logs</h3>

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
