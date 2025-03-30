import React, { useEffect, useState } from "react";
import { fetchNextMedication, fetchMissedDosesToday } from "../../services/api";
import axios from "axios";

const TopStats = () => {
  const [nextMedicationTime, setNextMedicationTime] = useState("");
  const [missedDosesToday, setMissedDosesToday] = useState(0);
  const [error, setError] = useState(null);

  // Function to fetch missed doses
  const fetchMissedDoses = async () => {
    try {
      const response = await fetchMissedDosesToday();
      
      const missedDoses = response.missedDosesToday

      console.log("Missed Doses NEW:", missedDoses);
      setMissedDosesToday(missedDoses);
      setError(null);
    } catch (error) {
      console.error("Error fetching missed doses:", error);
      
      // More detailed error logging
      if (error.response) {
        // The request was made and the server responded with a status code
        console.error("Error response data:", error.response.data);
        console.error("Error response status:", error.response.status);
      } else if (error.request) {
        // The request was made but no response was received
        console.error("No response received:", error.request);
      } else {
        // Something happened in setting up the request
        console.error("Error message:", error.message);
      }

      setMissedDosesToday(0);
      setError("Failed to fetch missed doses");
    }
  };

  useEffect(() => {
    // Fetch next medication time
    async function getNextMedication() {
      try {
        const data = await fetchNextMedication();
        setNextMedicationTime(data.nextMedicationTime);
      } catch (error) {
        console.error("Error fetching next medication time:", error);
        setNextMedicationTime("N/A");
      }
    }

    // Fetch missed doses
    fetchMissedDoses();

    // Set up interval to update missed doses every minute
    const intervalId = setInterval(fetchMissedDoses, 60000);

    // Initial fetch
    getNextMedication();

    // Cleanup interval on component unmount
    return () => clearInterval(intervalId);
  }, []);

  return (
    <div className="grid grid-cols-2 gap-6">
      <div className="p-6 rounded-lg shadow-md text-white bg-purple-500">
        <h3 className="text-lg">Next Medication Time</h3>
        <p className="text-3xl font-bold">
          {nextMedicationTime || "Loading..."}
        </p>
      </div>
      <div className="p-6 rounded-lg shadow-md text-white bg-pink-500">
        <h3 className="text-lg">Missed Doses Today</h3>
        <p className="text-3xl font-bold">
          {error ? "Error" : missedDosesToday}
        </p>
      </div>
    </div>
  );
};

export default TopStats;