import { API_BASE_URL, REQUEST_TIMEOUT_MS } from "./config";

/**
 * Centralized API client for the Construction Intelligence Platform.
 *
 * Every frontend feature calls this client. It never hardcodes frontend-only
 * results and always surfaces real backend responses or clear errors.
 */
const fetchJson = async (path, options = {}) => {
  const url = `${API_BASE_URL}${path}`;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const isJsonBody = typeof options.body === "string";
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        ...(isJsonBody ? { "Content-Type": "application/json" } : {}),
        ...options.headers,
      },
    });

    const contentType = response.headers.get("content-type") || "";
    let body = null;
    if (contentType.includes("application/json")) {
      body = await response.json();
    } else {
      body = { message: await response.text() };
    }

    if (!response.ok) {
      const error = new Error(
        (body && body.message) || "Request failed with status " + response.status
      );
      error.status = response.status;
      error.body = body;
      throw error;
    }

    return body;
  } catch (err) {
    if (err.name === "AbortError") {
      const timeoutError = new Error("Request timed out. The backend may be unavailable.");
      timeoutError.status = 504;
      error = timeoutError;
    }
    throw err;
  } finally {
    clearTimeout(timeoutId);
  }
};

export const api = {
  health: () => fetchJson("/health"),

  safety: (formData) =>
    fetchJson("/safety/analyze", {
      method: "POST",
      body: formData,
    }),

  crack: (formData) =>
    fetchJson("/crack/analyze", {
      method: "POST",
      body: formData,
    }),

  planning: (payload) =>
    fetchJson("/planning/project", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  valuation: (payload) =>
    fetchJson("/valuation/property", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  knowledge: (payload) =>
    fetchJson("/knowledge/ask", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  dailySite: (payload) =>
    fetchJson("/daily-site/plan", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  getDailySiteTasks: (planDate) =>
    fetchJson(`/daily-site/tasks?plan_date=${encodeURIComponent(planDate)}`, {
      method: "GET",
    }),

  patchDailyTaskComplete: (planDate, taskId, completed) =>
    fetchJson(
      `/daily-site/tasks/${encodeURIComponent(taskId)}/complete?plan_date=${encodeURIComponent(planDate)}`,
      {
        method: "PATCH",
        body: JSON.stringify({ task_id: taskId, completed }),
      }
    ),

  weather: (payload) =>
    fetchJson("/weather/advisory", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
};
