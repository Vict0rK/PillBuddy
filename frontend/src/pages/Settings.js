import React, { useEffect, useState } from "react";
import { addSetup, deletePatient } from "../services/api";
import { FaTrash, FaTimes, FaPenNib, FaPills, FaTools } from "react-icons/fa";
import { motion } from "framer-motion";
import FaceRecognition from "../components/setup/FaceRecognition"; // <--- Make sure this path is correct
import mqtt from "mqtt";

const Settings = ({ patientData }) => {
  // Basic patient info
  const [patientId, setPatientId] = useState("");
  const [name, setName] = useState("");
  const [faceData, setFaceData] = useState("");
  const [faceModel, setFaceModel] = useState("");

  // Medications array
  const [medications, setMedications] = useState([]);

  // Captured image for authentication
  const [capturedImage, setCapturedImage] = useState(null);

  // UI states
  const [activeTab, setActiveTab] = useState("medications"); // "medications" | "authentication"
  const [modalContent, setModalContent] = useState(null);

  // Setup MQTT variables
  const [client, setClient] = useState(null);
  const [publishMessage, setPublishMessage] = useState("");
  const [status, setStatus] = useState("Disconnected");

  // Load patient data when it’s available
  useEffect(() => {
    if (patientData) {
      setPatientId(patientData._id || "");
      setName(patientData.name || "");
      setFaceData(patientData.face_data || "");
      setMedications(patientData.medications || []);
      setFaceModel(patientData.face_model || "");
    }
  }, [patientData]);


  useEffect(() => {
    // Connect to the MQTT broker over WebSockets
    const mqttClient = mqtt.connect("ws://192.168.220.172:9001");
    setClient(mqttClient);

    mqttClient.on("connect", () => {
      setStatus("Connected");
      console.log("Connected to MQTT broker");
    });

    mqttClient.on("error", (err) => {
      console.error("MQTT Error:", err);
      mqttClient.end();
    });

    // Clean up on component unmount
    return () => {
      if (mqttClient) mqttClient.end();
    };
  }, []);



  // Switch tabs
  const handleTabSwitch = (tabName) => {
    setActiveTab(tabName);
  };

  // Add new medication
  const addMedication = () => {
    setMedications([
      ...medications,
      { name: "", timings: [""], dosage: "", unit: "g", stock: "", stockUnit: "g" }
    ]);
  };

  // Remove medication
  const removeMedication = (index) => {
    if (index === 0) {
      setModalContent({
        title: "Cannot Delete",
        message: "The first medication cannot be deleted!",
        type: "error",
      });
      return;
    }
    setMedications(medications.filter((_, i) => i !== index));
  };

  // Add timing
  const addTiming = (index) => {
    const updated = [...medications];
    updated[index].timings.push("");
    setMedications(updated);
  };

  // Remove timing
  const removeTiming = (medIndex, timeIndex) => {
    const updated = [...medications];
    updated[medIndex].timings.splice(timeIndex, 1);
    setMedications(updated);
  };

  // Handle medication field changes
  const handleMedicationChange = (index, field, value) => {
    const updated = [...medications];
    updated[index][field] = value;
    setMedications(updated);
  };

  
  // Delete entire patient
  const handleDeletePatient = () => {
    setModalContent({
      title: "Confirm Deletion",
      message: "Are you sure you want to delete this patient? This action cannot be undone.",
      type: "confirm",
      onConfirm: async () => {
        try {
          await deletePatient(patientId);
          localStorage.removeItem("patientId");
          setModalContent({
            title: "Patient Deleted",
            message: "Patient deleted. Redirecting to setup...",
            type: "success",
            onClose: () => (window.location.href = "/setup"),
          });
        } catch (err) {
          setModalContent({
            title: "Error",
            message: `Error deleting patient: ${err.message}`,
            type: "error",
          });
        }
      },
    });
  };


  const handleSaveAndUpload = async () => {
    // Validate medications
    let isValid = true;
    medications.forEach((med) => {
      if (
        !med.name.trim() ||
        !med.dosage.toString().trim() ||
        !med.stock.toString().trim() ||
        med.timings.length === 0 ||
        med.timings.some((t) => !t.trim())
      ) {
        isValid = false;
      }
    });
    if (!isValid) {
      setModalContent({
        title: "Missing Fields",
        message: "Please fill in all required fields in each medication card.",
        type: "error",
      });
      return;
    }
  
    // If authentication tab is active, require an image
    if (activeTab === "authentication" && !capturedImage) {
      setModalContent({
        title: "No Photo",
        message: "Please capture the patient's face before saving.",
        type: "error",
      });
      return;
    }

  
    // Build the updated patient object
    const updatedPatient = {
      patient_id: patientId,
      name,
      // Use capturedImage if available, otherwise fallback to faceData
      face_data: capturedImage !== null ? capturedImage : faceData,
      face_model: faceModel,
      medications,
    };

  
    try {

      // Save the patient settings
      await addSetup(updatedPatient);
  
      // After saving, ask for confirmation to upload to the Medication Box
      setModalContent({
        title: "Confirm Overwrite",
        message: "Are you sure you want to overwrite settings on the Medication Box?",
        type: "confirm",
        onConfirm: async () => {
          try {
            // Build the settings to be sent via MQTT
            const newSettings = { name: name, medications_to_take: medications, medication_list: ["Panadol", "Zyrtec"], face_model: faceModel};
  
            // Publish to MQTT pillbuddy/setup topic if connected
            if (client && client.connected) {
              client.publish(
                "pillbuddy/setup",
                JSON.stringify(newSettings),
                (error) => {
                  if (error) {
                    console.error("Publish error:", error);
                  } else {
                    console.log("Message published successfully:", JSON.stringify(newSettings));
                  }
                }
              );
            } else {
              console.error("MQTT client is not connected");
            }
  
            // Show success modal after uploading settings
            setModalContent({
              title: "Medication Box Settings Updated",
              message: "Settings have been uploaded to the Medication Box",
              type: "success",
              onClose: () => (window.location.href = "/setup"),
            });
          } catch (err) {
            setModalContent({
              title: "Error",
              message: `Failed to upload settings to Medication Box: ${err.message}`,
              type: "error",
            });
          }
        },
      });
    } catch (error) {
      setModalContent({
        title: "Error",
        message: `Error updating settings: ${error.message}`,
        type: "error",
      });
    }
  };
  

  // Callback for FaceRecognition to handle captured image
  const handleCapture = (imageData) => {
    setCapturedImage(imageData);
  };

  return (
    <div className="h-screen overflow-y-auto bg-gray-100 p-6">
      <h1 className="text-2xl font-bold mb-6">Settings</h1>

      {/* Patient Name Card */}
      <div className="bg-white shadow-md rounded-xl p-4 mb-6">
        <div className="flex items-center space-x-2 mb-4">
          <FaPenNib className="text-2xl text-gray-700" />
          <h3 className="text-xl font-semibold text-gray-700">Patient Name</h3>
        </div>
        <input
          type="text"
          className="border p-2 w-full"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
      </div>

      {/* Tabs: Medications / Authentication */}
      <div className="bg-white shadow-md rounded-xl p-4 mb-6">
        <div className="flex border-b">
          <button
            onClick={() => handleTabSwitch("medications")}
            className={`flex-1 py-2 text-center font-semibold ${
              activeTab === "medications"
                ? "border-b-4 border-blue-500 text-blue-500"
                : "text-gray-600"
            }`}
          >
            <FaPills className="inline mr-2" />
            Medications
          </button>
          <button
            onClick={() => handleTabSwitch("authentication")}
            className={`flex-1 py-2 text-center font-semibold ${
              activeTab === "authentication"
                ? "border-b-4 border-blue-500 text-blue-500"
                : "text-gray-600"
            }`}
          >
            <FaTools className="inline mr-2" />
            Authentication
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === "medications" && (
          <div className="mt-4">
            {medications.map((med, index) => (
              <div key={index} className="mb-6 bg-gray-50 p-4 rounded-md shadow relative">
                <div className="flex justify-between items-center">
                  <input
                    type="text"
                    placeholder="Medication Name"
                    value={med.name}
                    onChange={(e) => handleMedicationChange(index, "name", e.target.value)}
                    className="border p-2 w-full mb-2"
                  />
                  {index > 0 && (
                    <button
                      onClick={() => removeMedication(index)}
                      className="text-red-500 hover:text-red-700 ml-2"
                    >
                      <FaTrash />
                    </button>
                  )}
                </div>

                {/* Timings */}
                {med.timings.map((time, tIndex) => (
                  <div key={tIndex} className="flex items-center space-x-2 mb-2">
                    <input
                      type="time"
                      value={time}
                      onChange={(e) => {
                        const updated = [...medications];
                        updated[index].timings[tIndex] = e.target.value;
                        setMedications(updated);
                      }}
                      className="border p-2"
                    />
                    {med.timings.length > 1 && (
                      <button
                        onClick={() => removeTiming(index, tIndex)}
                        className="text-red-500 hover:text-red-700"
                      >
                        <FaTimes />
                      </button>
                    )}
                  </div>
                ))}
                <button
                  onClick={() => addTiming(index)}
                  className="text-blue-600 hover:text-blue-800"
                >
                  + Add Timing
                </button>

                {/* Dosage & Stock */}
                <div className="mt-2 flex space-x-2">
                  <input
                    type="number"
                    placeholder="Dosage"
                    value={med.dosage}
                    onChange={(e) => handleMedicationChange(index, "dosage", e.target.value)}
                    className="border p-2 w-full"
                  />
                  <select
                    value={med.unit}
                    onChange={(e) => handleMedicationChange(index, "unit", e.target.value)}
                    className="border p-2"
                  >
                    <option value="g">g</option>
                    <option value="ml">ml</option>
                  </select>
                </div>
                <div className="mt-2 flex space-x-2">
                  <input
                    type="number"
                    placeholder="Current Stock"
                    value={med.stock}
                    onChange={(e) => handleMedicationChange(index, "stock", e.target.value)}
                    className="border p-2 w-full"
                  />
                  <select
                    value={med.stockUnit}
                    onChange={(e) => handleMedicationChange(index, "stockUnit", e.target.value)}
                    className="border p-2"
                  >
                    <option value="g">g</option>
                    <option value="ml">ml</option>
                  </select>
                </div>
              </div>
            ))}

            <button
              onClick={addMedication}
              className="bg-pink-500 text-white py-2 px-4 rounded hover:bg-pink-600"
            >
              + Add Medication
            </button>
          </div>
        )}

        {activeTab === "authentication" && (
        <div className="mt-4 flex flex-col items-center">
            {/* <FaceRecognition
            existingImage={faceData}
            onCapture={(img) => setCapturedImage(img)}
            /> */}
            <FaceRecognition existingImage={capturedImage || faceData} onCapture={handleCapture} />
        </div>
        )}

      </div>

      {/* Action Buttons */}
      <div className="mt-6 flex space-x-4 justify-end">
        {/* <button
          className="bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700"
          onClick={handleUploadSettingsToMedicationBox}
        >
          Upload to Medication Box
        </button> */}
        <button
          className="bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700"
          onClick={handleSaveAndUpload}
        >
          Save Changes
        </button>
        <button
          className="bg-red-500 text-white py-2 px-4 rounded hover:bg-red-600"
          onClick={handleDeletePatient}
        >
          Delete Patient
        </button>
      </div>

      {/* Pop-up Modal */}
      {modalContent && (
        <motion.div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <motion.div className="bg-white p-6 rounded-lg shadow-lg text-center" initial={{ scale: 0.8 }} animate={{ scale: 1 }}>
            <h2 className={`text-lg font-semibold ${modalContent.type === "error" ? "text-red-600" : "text-green-600"}`}>
              {modalContent.title}
            </h2>
            <p className="text-gray-700 mt-2">{modalContent.message}</p>
            <div className="mt-4">
              {modalContent.type === "confirm" ? (
                <>
                  <button className="bg-red-500 text-white px-4 py-2 rounded mr-2 hover:bg-red-600" onClick={modalContent.onConfirm}>
                    Confirm
                  </button>
                  <button className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600" onClick={() => setModalContent(null)}>
                    Cancel
                  </button>
                </>
              ) : (
                <button
                  className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                  onClick={() => {
                    if (modalContent.onClose) modalContent.onClose();
                    setModalContent(null);
                  }}
                >
                  OK
                </button>
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </div>
  );
};

export default Settings;
