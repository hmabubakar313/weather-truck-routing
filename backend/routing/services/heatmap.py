"""Build 0-48h weather heatmap data along a route corridor, pre-fetched for client-side slicing."""

from datetime import timezone

from .risk import classify_checkpoint
from .weather import fetch_hourly_forecast_many, forecast_days_for, nearest_hour_index

FORECAST_HOURS = 48


def build_corridor_heatmap(checkpoints, departure_dt, load_lb):
    """checkpoints: list of {lon, lat, distance_miles}. Returns, per checkpoint, a
    48-entry series of {hour_offset, wind_mph, rain_in_hr, snow_in_hr, risk}."""
    departure_dt = departure_dt.astimezone(timezone.utc)
    forecast_days = forecast_days_for(departure_dt, extra_hours=FORECAST_HOURS)
    hourly_blocks = fetch_hourly_forecast_many(
        [(cp["lat"], cp["lon"]) for cp in checkpoints], forecast_days=forecast_days,
    )
    series = []
    for cp, hourly in zip(checkpoints, hourly_blocks):
        start_idx = nearest_hour_index(hourly["time"], departure_dt)
        points = []
        for offset in range(0, FORECAST_HOURS + 1):
            idx = start_idx + offset
            if idx >= len(hourly["time"]):
                break
            wind = hourly["wind_speed_10m"][idx]
            rain = hourly["rain"][idx]
            snow_in = hourly["snowfall"][idx] / 2.54
            points.append({
                "hour_offset": offset,
                "time": hourly["time"][idx],
                "wind_mph": wind,
                "rain_in_hr": rain,
                "snow_in_hr": snow_in,
                "risk": classify_checkpoint(wind, rain, snow_in, load_lb),
            })
        series.append({
            "lon": cp["lon"],
            "lat": cp["lat"],
            "distance_miles": cp["distance_miles"],
            "forecast": points,
        })
    return series
