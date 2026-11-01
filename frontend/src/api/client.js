const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function messageFromErrorBody(body) {
  if (!body || typeof body !== "object") return "Failed to plan routes";
  if (typeof body.error === "string") return body.error;
  // DRF validation errors look like { field: ["message", ...], ... }
  const fieldErrors = Object.entries(body)
    .filter(([, value]) => Array.isArray(value))
    .map(([field, messages]) => `${field}: ${messages.join(", ")}`);
  return fieldErrors.length ? fieldErrors.join("; ") : "Failed to plan routes";
}

export async function planRoutes({ origin, destination, departureTime, loadWeightLb }) {
  let res;
  try {
    res = await fetch(`${API_BASE}/api/routes/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        origin,
        destination,
        departure_time: departureTime,
        load_weight_lb: loadWeightLb,
      }),
    });
  } catch {
    throw new Error("Could not reach the server. Check your connection and try again.");
  }

  let body = null;
  try {
    body = await res.json();
  } catch {
    // non-JSON response, fall through to generic message below
  }

  if (!res.ok) {
    throw new Error(messageFromErrorBody(body));
  }
  return body;
}
