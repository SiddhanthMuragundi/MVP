import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("tdc_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && !location.pathname.startsWith("/login")) {
      localStorage.removeItem("tdc_token");
      localStorage.removeItem("tdc_user");
      location.assign("/login");
    }
    return Promise.reject(error);
  },
);

export default api;
