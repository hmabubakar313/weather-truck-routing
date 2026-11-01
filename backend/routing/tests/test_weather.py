from datetime import datetime, timedelta, timezone

import pytest

from routing.services.weather import MAX_FORECAST_DAYS, WeatherError, forecast_days_for


def test_forecast_days_covers_near_future_departure():
    departure = datetime.now(timezone.utc) + timedelta(hours=10)
    days = forecast_days_for(departure, extra_hours=48)
    assert days >= 3  # 10h to departure + 48h lookahead must fit inside the fetched window


def test_forecast_days_covers_departure_several_days_out():
    departure = datetime.now(timezone.utc) + timedelta(days=4)
    days = forecast_days_for(departure, extra_hours=48)
    assert days >= 7  # 4 days out + 48h lookahead


def test_forecast_days_clamps_past_departure_to_minimum():
    departure = datetime.now(timezone.utc) - timedelta(days=300)
    assert forecast_days_for(departure, extra_hours=48) == 1


def test_forecast_days_raises_beyond_open_meteo_horizon():
    departure = datetime.now(timezone.utc) + timedelta(days=MAX_FORECAST_DAYS + 5)
    with pytest.raises(WeatherError):
        forecast_days_for(departure, extra_hours=48)
