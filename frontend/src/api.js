import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export async function askAgent(message) {
  const response = await axios.post(`${API_BASE_URL}/chat`, {
    message,
  });

  return response.data;
}

export async function getHealth() {
  const response = await axios.get(`${API_BASE_URL}/health`);
  return response.data;
}