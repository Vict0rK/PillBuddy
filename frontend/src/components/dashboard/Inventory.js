import React, { useEffect, useState } from "react";
import mqtt from "mqtt";
import { fetchMedicationsByPatient, updateMedicationWeight } from "../../services/api";

const Inventory = ({ patientId }) => {
  const [medications, setMedications] = useState([]);
  const [medicationTaken, setMedicationTaken] = useState("");
  const [updatedWeightDiff, setUpdatedWeightDiff] = useState(null);

  // Fetch medications for the patient
  const loadMedications = async () => {
    try {
      if (!patientId) return;
      const data = await fetchMedicationsByPatient(patientId);
      setMedications(data);
    } catch (error) {
      console.error("Error fetching medications:", error);
    }
  };

  useEffect(() => {
    loadMedications();
  }, [patientId]);

  // Set up MQTT subscriptions to "medication_taken" and "updated_weight"
  useEffect(() => {
    const topics = ["pillbuddy/medication_taken", "pillbuddy/updated_weight"];
    const client = mqtt.connect("ws://192.168.220.172:9001");

    client.on("connect", () => {
      console.log("Connected to MQTT broker for Inventory");
      client.subscribe(topics, (err) => {
        if (err) {
          console.error("Error subscribing to topics:", err);
        } else {
          console.log(`Subscribed to topics: ${topics.join(", ")}`);
        }
      });
    });

    client.on("message", async (topic, messageBuffer) => {
      const message = messageBuffer.toString();
      console.log(`Received message on topic ${topic}: ${message}`);

      if (topic === "pillbuddy/medication_taken") {
        // Save the medication name taken from text_detection.py
        setMedicationTaken(message);
      } else if (topic === "pillbuddy/updated_weight") {
        // Expect a JSON payload like: { "medication": "Aspirin", "difference": 20 }
        try {
          const parsed = JSON.parse(message);
          const { medication, difference } = parsed;
          setUpdatedWeightDiff(difference);

          // Update the medication's stock by subtracting the difference
          let newStock = 0;
          setMedications((prevMeds) =>
            prevMeds.map((med) => {
              if (med.name.toLowerCase() === medication.toLowerCase()) {
                const currentStock = parseFloat(med.stock);
                newStock = currentStock - difference;
                return { ...med, stock: newStock };
              }
              return med;
            })
          );

          // Call API PUT request to update the medication weight (new stock) in the DB
          try {
            await updateMedicationWeight(patientId, medication, newStock);
          } catch (apiError) {
            console.error("Error updating medication weight:", apiError);
          }
        } catch (e) {
          console.error("Error parsing updated_weight message:", e);
        }
      }
    });

    client.on("error", (err) => {
      console.error("MQTT error in Inventory:", err);
    });

    return () => {
      topics.forEach((topic) => client.unsubscribe(topic));
      client.end();
    };
  }, [patientId]);

  return (
    <div className="bg-white p-6 rounded-lg shadow-md w-full">
      <h3 className="text-lg font-semibold mb-4">Inventory</h3>

      {/* Optionally display the latest medication taken and weight difference */}
      {medicationTaken && (
        <div className="mb-4">
          <strong>Medication Taken:</strong> {medicationTaken}
        </div>
      )}
      {updatedWeightDiff !== null && (
        <div className="mb-4">
          <strong>Weight Difference:</strong> {updatedWeightDiff} g
        </div>
      )}

      <ul>
        {medications.map((med, index) => {
          const stockValue = parseFloat(med.stock);
          return (
            <li
              key={index}
              className={`flex justify-between py-2 ${
                stockValue < 10 ? "text-red-500" : "text-gray-700"
              }`}
            >
              <span>{med.name}</span>
              <span>
                {med.stock}
                {med.stockUnit} left
              </span>
            </li>
          );
        })}
      </ul>
    </div>
  );
};

export default Inventory;
