import React, { useEffect, useState } from "react";
import { fetchMedicationsByPatient } from "../../services/api";

const Inventory = ({ patientId }) => {
  const [medications, setMedications] = useState([]);

  useEffect(() => {
    const getMedications = async () => {
      try {
        if (!patientId) return;
        const data = await fetchMedicationsByPatient(patientId);
        setMedications(data);
      } catch (error) {
        console.error("Error fetching medications:", error);
      }
    };
    getMedications();
  }, [patientId]);

  return (
    <div className="bg-white p-6 rounded-lg shadow-md w-full">
      <h3 className="text-lg font-semibold mb-4">Inventory</h3>
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
                {med.stock}{med.stockUnit} left
              </span>
            </li>
          );
        })}
      </ul>
    </div>
  );
};

export default Inventory;
