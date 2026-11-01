import { useState } from "react";

export default function TripForm({ onSubmit, loading }) {
  const [origin, setOrigin] = useState("");
  const [destination, setDestination] = useState("");
  const [departureTime, setDepartureTime] = useState("");
  const [loadWeightLb, setLoadWeightLb] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    onSubmit({
      origin,
      destination,
      departureTime: new Date(departureTime).toISOString(),
      loadWeightLb: Number(loadWeightLb),
    });
  }

  return (
    <form className="trip-form" onSubmit={handleSubmit}>
      <label>
        Origin
        <input value={origin} onChange={(e) => setOrigin(e.target.value)} placeholder="Minneapolis, MN" required />
      </label>
      <label>
        Destination
        <input value={destination} onChange={(e) => setDestination(e.target.value)} placeholder="Chicago, IL" required />
      </label>
      <label>
        Departure date/time
        <input type="datetime-local" value={departureTime} onChange={(e) => setDepartureTime(e.target.value)} required />
      </label>
      <label>
        Load weight (lb)
        <input type="number" min="0" value={loadWeightLb} onChange={(e) => setLoadWeightLb(e.target.value)} required />
      </label>
      <button type="submit" disabled={loading}>
        {loading ? "Planning..." : "Plan Route"}
      </button>
    </form>
  );
}
