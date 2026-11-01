import { useState } from "react";
import { planRoutes } from "./api/client";
import TripForm from "./components/TripForm";
import RouteMap from "./components/RouteMap";
import RouteSummary from "./components/RouteSummary";
import WeatherHeatmap from "./components/WeatherHeatmap";
import Toast from "./components/Toast";
import "./App.css";

export default function App() {
  const [result, setResult] = useState(null);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [hourOffset, setHourOffset] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(trip) {
    setLoading(true);
    setError(null);
    try {
      const data = await planRoutes(trip);
      setResult(data);
      setSelectedIndex(data.recommended_index);
      setHourOffset(0);
    } catch (err) {
      setError(err.message || "Something went wrong while planning the route.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header>
        <h1>Weather-Aware Truck Routing</h1>
      </header>

      <div className="app-body">
        <aside className="sidebar">
          <TripForm onSubmit={handleSubmit} loading={loading} />
          {result && (
            <>
              <RouteSummary
                routes={result.routes}
                recommendedIndex={result.recommended_index}
                selectedIndex={selectedIndex}
                onSelect={setSelectedIndex}
              />
              <WeatherHeatmap hourOffset={hourOffset} onChange={setHourOffset} />
            </>
          )}
        </aside>

        <main className="map-pane">
          {result ? (
            <RouteMap
              origin={result.origin}
              destination={result.destination}
              routes={result.routes}
              selectedIndex={selectedIndex}
              recommendedIndex={result.recommended_index}
              heatmap={result.heatmap}
              hourOffset={hourOffset}
            />
          ) : (
            <div className="map-placeholder">Enter a trip to see routes and weather risk.</div>
          )}
        </main>
      </div>

      <Toast message={error} onClose={() => setError(null)} />
    </div>
  );
}
