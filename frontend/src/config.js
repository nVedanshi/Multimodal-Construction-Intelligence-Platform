export const API_BASE_URL =
  (typeof import.meta !== "undefined" && import.meta.env.VITE_API_BASE_URL)
    ? import.meta.env.VITE_API_BASE_URL
    : "/api";

export const REQUEST_TIMEOUT_MS = 60000;
