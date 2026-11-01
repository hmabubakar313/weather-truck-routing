import { CircleMarker, MapContainer, Polyline, Popup, Tooltip, TileLayer, useMap } from "react-leaflet";
import { useEffect } from "react";
import { RISK_COLORS, ROUTE_COLORS } from "../constants";

function FitBounds({ bounds }) {
  const map = useMap();
  useEffect(() => {
    if (bounds.length) map.fitBounds(bounds, { padding: [30, 30] });
  }, [bounds, map]);
  return null;
}

function toLatLngs(geometry) {
  return geometry.map(([lon, lat]) => [lat, lon]);
}

export default function RouteMap({ origin, destination, routes, selectedIndex, recommendedIndex, heatmap, hourOffset }) {
  const bounds = [
    [origin.lat, origin.lon],
    [destination.lat, destination.lon],
    ...routes.flatMap((r) => toLatLngs(r.geometry)),
  ];

  return (
    <MapContainer center={[origin.lat, origin.lon]} zoom={6} className="route-map">
      <TileLayer
        attribution='&copy; OpenStreetMap contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <FitBounds bounds={bounds} />

      {routes.map((route, i) => (
        <Polyline
          key={i}
          positions={toLatLngs(route.geometry)}
          pathOptions={{
            color: ROUTE_COLORS[i % ROUTE_COLORS.length],
            weight: i === selectedIndex ? 5 : 3,
            opacity: i === selectedIndex ? 1 : 0.4,
          }}
        />
      ))}

      {routes[selectedIndex]?.checkpoints.map((cp, i) => (
        <CircleMarker
          key={i}
          center={[cp.lat, cp.lon]}
          radius={6}
          pathOptions={{ color: RISK_COLORS[cp.risk], fillColor: RISK_COLORS[cp.risk], fillOpacity: 0.9 }}
        >
          <Popup>
            <div>
              <strong>Mile {cp.distance_miles}</strong>
              <div>Risk: {cp.risk}</div>
              <div>ETA: {new Date(cp.eta).toLocaleString()}</div>
              <div>Wind: {cp.weather.wind_mph.toFixed(1)} mph</div>
              <div>Rain: {cp.weather.rain_in_hr.toFixed(2)} in/hr</div>
              <div>Snow: {cp.weather.snow_in_hr.toFixed(2)} in/hr</div>
            </div>
          </Popup>
        </CircleMarker>
      ))}

      {heatmap.map((point, i) => {
        const forecastPoint = point.forecast.find((f) => f.hour_offset === hourOffset);
        if (!forecastPoint) return null;
        return (
          <CircleMarker
            key={`heat-${i}`}
            center={[point.lat, point.lon]}
            radius={16}
            pathOptions={{
              color: RISK_COLORS[forecastPoint.risk],
              fillColor: RISK_COLORS[forecastPoint.risk],
              fillOpacity: 0.45,
              weight: 2,
            }}
          >
            <Tooltip direction="top" offset={[0, -10]}>
              <div>
                <strong>+{forecastPoint.hour_offset}h — {forecastPoint.risk}</strong>
                <div>Wind: {forecastPoint.wind_mph.toFixed(1)} mph</div>
                <div>Rain: {forecastPoint.rain_in_hr.toFixed(2)} in/hr</div>
                <div>Snow: {forecastPoint.snow_in_hr.toFixed(2)} in/hr</div>
              </div>
            </Tooltip>
          </CircleMarker>
        );
      })}
    </MapContainer>
  );
}
