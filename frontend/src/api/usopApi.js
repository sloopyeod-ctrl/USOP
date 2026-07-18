import axios from "axios";

const apiBaseUrl = (
  import.meta.env.VITE_API_BASE_URL
  || "http://127.0.0.1:8000"
).replace(/\/$/, "");

const api = axios.create({
  baseURL: apiBaseUrl,
});

export default api;
