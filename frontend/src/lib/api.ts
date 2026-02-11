import axios from "axios";

// Vite convention: VITE_API_BASE_URL (e.g. http://127.0.0.1:8005)
// If unset, default to same-origin.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("authToken");
  if (token) {
    config.headers = config.headers ?? {};
    // DRF token auth
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

export const authAPI = {
  getProfile: () => client.get("/api/v1/auth/profile/"),
};

export const analyticsAPI = {
  getLeadSummary: () => client.get("/api/v1/analytics/leads/summary/"),
};
