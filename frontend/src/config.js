const API_BASE_URL =
  window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
    ? "http://localhost:5000/api" // Use localhost when running on your Pi
    : "http://172.20.10.2:5000/api"; // Use Pi's IP when accessed remotely

export default API_BASE_URL;