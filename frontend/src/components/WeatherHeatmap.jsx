export default function WeatherHeatmap({ hourOffset, onChange, maxHours = 48 }) {
  return (
    <div className="heatmap-slider">
      <label htmlFor="hour-offset">Forecast: +{hourOffset}h</label>
      <input
        id="hour-offset"
        type="range"
        min={0}
        max={maxHours}
        step={1}
        value={hourOffset}
        onChange={(e) => onChange(Number(e.target.value))}
      />
    </div>
  );
}
