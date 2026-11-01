import { ROUTE_COLORS } from "../constants";

function formatDuration(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.round((seconds % 3600) / 60);
  return `${hours}h ${minutes}m`;
}

export default function RouteSummary({ routes, recommendedIndex, selectedIndex, onSelect }) {
  return (
    <div className="route-summary-list">
      {routes.map((route, i) => (
        <button
          key={i}
          className={`route-card ${selectedIndex === i ? "selected" : ""} ${recommendedIndex === i ? "recommended" : ""}`}
          style={{ borderColor: ROUTE_COLORS[i % ROUTE_COLORS.length] }}
          onClick={() => onSelect(i)}
        >
          <div className="route-card-title">
            Route {i + 1} {recommendedIndex === i && <span className="badge">Recommended</span>}
          </div>
          <div className="route-card-stats">
            <span>{route.distance_miles} mi</span>
            <span>{formatDuration(route.duration_seconds)}</span>
          </div>
          <div className="route-card-risk">
            <span>Severe miles: {route.metrics.severe_miles}</span>
            <span>High miles: {route.metrics.high_miles}</span>
            <span>Avg risk score: {route.metrics.avg_risk_score}</span>
          </div>
        </button>
      ))}
    </div>
  );
}
