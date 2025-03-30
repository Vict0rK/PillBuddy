import axios from "axios";

const BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://localhost:5000/api";

// Backend base URL
const API = axios.create({
    baseURL: BASE_URL,
  });
  
  

// API calls
export const fetchMedications = async () => {
  const response = await API.get("/medications");
  return response.data;
};

export const addMedication = async (medication) => {
  const response = await API.post("/medications", medication);
  return response.data;
};

export const fetchLogs = async () => {
    const response = await API.get("/logs");
    return response.data;
  };

export const addLog = async (log) => {
  const response = await API.post("/logs", log);
  return response.data;
};

export const fetchNotifications = async () => {
  const response = await API.get("/notifications");
  return response.data;
};

export const clearNotifications = async () => {
  const response = await API.delete("/notifications");
  return response.data;
};

export const fetchSetup = async () => {
  const response = await API.get("/setup");
  return response.data;
};


export const addSetup = async (data) => {
  const response = await API.post("/setup", data);
  return response.data;
};

export const fetchMedicationsByPatient = async (patientId) => {
  const response = await API.get(`/medications/${patientId}`);
  return response.data;
}

export const deletePatient = async (patientId) => {
  const response = await API.delete(`/patients/${patientId}`);
  return response.data;
};

export const fetchNextMedication = async () => {
  const response = await API.get("/next-medication");
  return response.data;
};

export const fetchMissedDosesToday = async () => {
    const response = await API.get("/missed-doses");
    return response.data;
};

export const fetchWeeklyAdherenceData = async () => {
    const response = await API.get("/weekly-adherence");
    return response.data;
};

