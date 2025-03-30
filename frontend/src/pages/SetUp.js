import React, { useState } from "react";
import { addSetup } from "../services/api";
import FaceRecognition from "../components/setup/FaceRecognition";
import { motion } from "framer-motion";
import { FaTrash, FaTimes } from "react-icons/fa";
import logo from "../assets/images/logo.png";

const SetUp = () => {
  const [step, setStep] = useState(1);
  const [patientName, setPatientName] = useState("");
  const [medications, setMedications] = useState([
    { name: "", timings: [""], dosage: "", unit: "g", stock: "", stockUnit: "g" }
  ]);
  const [capturedImage, setCapturedImage] = useState(null);
  const [errors, setErrors] = useState({});
  const [modalContent, setModalContent] = useState(null);

  const nextStep = () => {
    if (step === 1 && !patientName.trim()) {
      setModalContent({
        title: "Missing Name",
        message: "Please enter a name for the patient.",
        type: "error",
      })
      return;
    }
    if (step === 2) {
      let isValid = true;
      medications.forEach((med, index) => {
        let medErrors = {};
        if (!med.name.trim()) {
          isValid = false;
        }
        if (!med.dosage) {
          isValid = false;
        }
        if (!med.stock) {
          isValid = false;
        }
        if (med.timings.length === 0 || med.timings.some(time => !time.trim())) {
          isValid = false;
        }
      });
      if (!isValid) {
        setModalContent({
            title: "⚠️ Missing Fields",
            message: "Please fill in all required fields in each medication card.",
            type: "error",
        })
        return;
      }
    }
    setStep(prev => prev + 1);
  };

  const prevStep = () => setStep(prev => prev - 1);

  const handleMedicationChange = (index, field, value) => {
    const updated = [...medications];
    updated[index][field] = value;
    setMedications(updated);
  };

  const addTiming = (index) => {
    const updated = [...medications];
    updated[index].timings.push("");
    setMedications(updated);
  };

  const removeTiming = (medIndex, timeIndex) => {
    const updated = [...medications];
    updated[medIndex].timings.splice(timeIndex, 1);
    setMedications(updated);
  };

  const addMedication = () => {
    setMedications([...medications, { name: "", timings: [""], dosage: "", unit: "g", stock: "", stockUnit: "g" }]);
  };

  const removeMedication = (index) => {
    setMedications(medications.filter((_, i) => i !== index));
  };

  const handleCapture = (imgData) => {
    setCapturedImage(imgData);
  };

  const handleSubmit = async () => {
    try {
      if (!capturedImage) {
          setModalContent({
              title: "No Photo",
              message: "Please take a photo of the patient.",
              type: "error",
          });
          return;
      }
      const response = await addSetup({
        name: patientName,
        face_data: capturedImage,
        medications
      });
      if (response.patient_id) {
        localStorage.setItem("patientId", response.patient_id);
      }
      setModalContent({
        title: "Success",
        message: "Setup saved successfully!",
        type: "success",
        onClose: () => {
          setModalContent(null);
          setTimeout(() => window.location.reload(), 300);
        },
      });
    } catch (error) {
      console.error("Error saving setup:", error);
      setModalContent({
        title: "Error",
        message: `Error saving setup: ${error.message}`,
        type: "error",
      });
    }
  };

  return (
    <div className="min-h-screen flex justify-center items-center bg-[#0E1B30] text-white">
      <motion.div
        className="w-full max-w-3xl bg-[#1A2A47] p-8 rounded-lg shadow-lg m-20"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Logo */}
        <div className="flex justify-center mb-4">
          <img src={logo} alt="PillBuddy Logo" className="w-40 h-auto" />
        </div>

        {step === 1 && (
          <motion.div
            className="text-center"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4 }}
          >
            <h2 className="text-3xl font-bold mb-4">Enter Patient's Name</h2>
            <input
              type="text"
              placeholder="Patient's Name"
              value={patientName}
              onChange={(e) => setPatientName(e.target.value)}
              className="p-3 border rounded w-full bg-[#22365B] text-white placeholder-gray-400 mb-4 text-center"
            />
            <button onClick={nextStep} className="bg-[#7D5FFF] text-white py-3 px-6 rounded hover:bg-[#5A3EC8] transition-all">
              Next
            </button>
          </motion.div>
        )}

        {step === 2 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4 }}
          >
            <h2 className="text-2xl font-bold mb-4">Enter Medication Details</h2>
            {medications.map((med, index) => (
              <div key={index} className="mb-6 bg-[#22365B] p-4 rounded-md shadow relative">
                <div className="flex justify-between">
                  <input
                    type="text"
                    placeholder="Medication Name"
                    value={med.name}
                    onChange={(e) => handleMedicationChange(index, "name", e.target.value)}
                    className="p-3 border rounded w-full bg-[#2C4B74] text-white placeholder-gray-400 mb-2"
                  />
                  {index > 0 && (
                    <button
                      onClick={() => removeMedication(index)}
                      className="text-red-400 hover:text-red-600 absolute right-[-30px] top-1/2 transform -translate-y-1/2"
                    >
                      <FaTrash />
                    </button>
                  )}
                </div>

                {med.timings.map((time, timeIndex) => (
                  <div key={timeIndex} className="flex items-center space-x-2 mb-2">
                    <input
                      type="time"
                      value={time}
                      onChange={(e) => {
                        const updated = [...medications];
                        updated[index].timings[timeIndex] = e.target.value;
                        setMedications(updated);
                      }}
                      className="p-3 border rounded bg-[#2C4B74] text-white"
                    />
                    {med.timings.length > 1 && (
                      <button
                        onClick={() => removeTiming(index, timeIndex)}
                        className="text-white hover:text-gray-400"
                      >
                        <FaTimes />
                      </button>
                    )}
                  </div>
                ))}
                <button onClick={() => addTiming(index)} className="text-blue-400 hover:text-blue-500">
                  + Add Timing
                </button>

                <div className="flex space-x-2 mt-2">
                  <input
                    type="number"
                    placeholder="Dosage"
                    value={med.dosage}
                    onChange={(e) => handleMedicationChange(index, "dosage", e.target.value)}
                    className="p-3 border rounded w-full bg-[#2C4B74] text-white"
                  />
                  <select
                    value={med.unit}
                    onChange={(e) => handleMedicationChange(index, "unit", e.target.value)}
                    className="p-3 border rounded bg-[#2C4B74] text-white"
                  >
                    <option value="g">g</option>
                    <option value="ml">ml</option>
                  </select>
                </div>
                <div className="flex space-x-2 mt-2">
                  <input
                    type="number"
                    placeholder="Current Stock"
                    value={med.stock}
                    onChange={(e) => handleMedicationChange(index, "stock", e.target.value)}
                    className="p-3 border rounded w-full bg-[#2C4B74] text-white"
                  />
                  <select
                    value={med.stockUnit}
                    onChange={(e) => handleMedicationChange(index, "stockUnit", e.target.value)}
                    className="p-3 border rounded bg-[#2C4B74] text-white"
                  >
                    <option value="g">g</option>
                    <option value="ml">ml</option>
                  </select>
                </div>
              </div>
            ))}
            <button
              onClick={addMedication}
              className="bg-[#FF57A1] text-white p-2 rounded hover:bg-[#D94786] transition-all"
            >
              + Add Medication
            </button>
            <div className="flex justify-between mt-6">
              <button
                onClick={prevStep}
                className="bg-gray-500 text-white p-3 rounded hover:bg-gray-600 transition-all"
              >
                Back
              </button>
              <button
                onClick={nextStep}
                className="bg-[#7D5FFF] text-white p-3 rounded hover:bg-[#5A3EC8] transition-all"
              >
                Next
              </button>
            </div>
          </motion.div>
        )}

        {step === 3 && (
          <motion.div
            className="text-center"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4 }}
          >
            <h2 className="text-2xl font-bold mb-4">Register Patient's Face</h2>
            <p className="text-s mb-10">Please capture a photo of the patient's face.</p>
            <div className="flex justify-center">
              {capturedImage ? (
                <img src={capturedImage} alt="Captured Face" className="mx-auto rounded-md" />
              ) : (
                // <FaceRecognition onCapture={handleCapture} />
                <FaceRecognition existingImage={capturedImage} onCapture={handleCapture} />

              )}
            </div>
            {capturedImage && (
              <button
                onClick={() => setCapturedImage(null)}
                className="mt-4 bg-red-500 text-white p-2 rounded hover:bg-red-600 transition-all"
              >
                Retake Image
              </button>
            )}
            <div className="flex justify-between mt-6">
              <button
                onClick={prevStep}
                className="bg-gray-500 text-white p-3 rounded hover:bg-gray-600 transition-all"
              >
                Back
              </button>
              <button
                onClick={handleSubmit}
                className="bg-[#7D5FFF] text-white p-3 rounded hover:bg-[#5A3EC8] transition-all"
              >
                Save Setup
              </button>
            </div>
          </motion.div>
        )}
      </motion.div>
       {/* Pop-up Modal */}
       {modalContent && (
        <motion.div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <motion.div className="bg-white p-6 rounded-lg shadow-lg text-center" initial={{ scale: 0.8 }} animate={{ scale: 1 }}>
            <h2 className={`text-lg font-semibold ${modalContent.type === "error" ? "text-red-600" : "text-green-600"}`}>
              {modalContent.title}
            </h2>
            <p className="text-gray-700 mt-2">{modalContent.message}</p>
            <button className="bg-blue-500 text-white px-4 py-2 rounded mt-4" onClick={() => {
              if (modalContent.onClose) modalContent.onClose();
              setModalContent(null);
            }}>OK</button>
          </motion.div>
        </motion.div>
      )}
    </div>
  );
};

export default SetUp;
