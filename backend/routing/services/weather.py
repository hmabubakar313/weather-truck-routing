"""Open-Meteo client: hourly forecast lookup, no API key required."""

import math
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import httpx

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
HOURLY_VARS = "wind_speed_10m,precipitation,rain,snowfall"
MAX_FORECAST_DAYS = 16


class WeatherError(Exception):
    pass


def forecast_days_for(departure_dt, extra_hours=48):
    """Open-Meteo's forecast_days window must stretch from today through departure
    time plus the heatmap's lookahead (default 48h), or late checkpoints/heatmap
    hours fall outside the fetched data and silently clamp to the last hour we have."""
    now = datetime.now(timezone.utc)
    hours_ahead = (departure_dt.astimezone(timezone.utc) - now).total_seconds() / 3600 + extra_hours
    days = max(1, math.ceil(hours_ahead / 24) + 1)
    if days > MAX_FORECAST_DAYS:
        raise WeatherError(
            f"departure is too far in the future for weather forecasting (max {MAX_FORECAST_DAYS} days ahead)"
        )
    return days


def fetch_hourly_forecast(lat, lon, forecast_days=3):
    """Return the raw Open-Meteo hourly block for one location, wind in mph, rain/snow in in/hr."""
    try:
        resp = httpx.get(
            OPEN_METEO_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "hourly": HOURLY_VARS,
                "wind_speed_unit": "mph",
                "precipitation_unit": "inch",
                "forecast_days": forecast_days,
                "timezone": "UTC",
            },
            timeout=15,
        )
    except httpx.HTTPError as exc:
        raise WeatherError(f"could not reach Open-Meteo: {exc}") from exc
    if resp.status_code != 200:
        raise WeatherError(f"weather lookup failed for ({lat},{lon}): {resp.status_code} {resp.text}")
    return resp.json()["hourly"]


def fetch_hourly_forecast_many(points, forecast_days=3):
    """points: list of (lat, lon). Fetches concurrently (each call is a separate blocking
    HTTP request) and returns the hourly blocks in the same order."""
    with ThreadPoolExecutor(max_workers=8) as pool:
        return list(pool.map(lambda p: fetch_hourly_forecast(p[0], p[1], forecast_days), points))


def nearest_hour_index(hourly_times, target_dt):
    target = target_dt.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0)
    parsed = [datetime.fromisoformat(t).replace(tzinfo=timezone.utc) for t in hourly_times]
    diffs = [abs((t - target).total_seconds()) for t in parsed]
    return diffs.index(min(diffs))


def weather_at(hourly, target_dt):
    """Pick the forecast hour closest to target_dt and return wind/rain/snow rates."""
    idx = nearest_hour_index(hourly["time"], target_dt)
    rain = hourly["rain"][idx]
    snow_in = hourly["snowfall"][idx] / 2.54  # snowfall is always in cm, independent of precipitation_unit
    return {
        "wind_mph": hourly["wind_speed_10m"][idx],
        "rain_in_hr": rain,
        "snow_in_hr": snow_in,
        "forecast_time": hourly["time"][idx],
    }
