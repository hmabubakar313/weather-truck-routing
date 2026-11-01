from unittest.mock import patch

import pytest
from rest_framework.test import APIClient

FAKE_ROUTES = [
    {"geometry": [[-93.0, 45.0], [-92.5, 44.5], [-92.0, 44.0]], "distance_m": 80_000, "duration_s": 5400},
    {"geometry": [[-93.0, 45.0], [-92.7, 44.6], [-92.0, 44.0]], "distance_m": 85_000, "duration_s": 5600},
]

FAKE_HOURLY = {
    "time": ["2026-01-01T00:00", "2026-01-01T01:00", "2026-01-01T02:00", "2026-01-01T03:00"],
    "wind_speed_10m": [10, 12, 15, 11],
    "precipitation": [0, 0, 0, 0],
    "rain": [0, 0, 0, 0],
    "snowfall": [0, 0, 0, 0],
}


@pytest.mark.django_db
@patch("routing.services.weather.fetch_hourly_forecast", return_value=FAKE_HOURLY)
@patch("routing.views.ors.get_routes", return_value=FAKE_ROUTES)
@patch("routing.views.ors.geocode")
def test_plan_routes_returns_recommendation(mock_geocode, mock_get_routes, mock_weather):
    mock_geocode.side_effect = [(-93.0, 45.0), (-92.0, 44.0)]
    client = APIClient()
    resp = client.post("/api/routes/", {
        "origin": "Minneapolis, MN",
        "destination": "Rochester, MN",
        "departure_time": "2026-01-01T00:00:00Z",
        "load_weight_lb": 20000,
    }, format="json")

    assert resp.status_code == 200
    body = resp.json()
    assert len(body["routes"]) == 2
    assert "recommended_index" in body
    assert body["routes"][0]["checkpoints"]
    assert all("risk" in cp for cp in body["routes"][0]["checkpoints"])
    assert "heatmap" in body


@pytest.mark.django_db
def test_plan_routes_validates_input():
    client = APIClient()
    resp = client.post("/api/routes/", {"origin": "A"}, format="json")
    assert resp.status_code == 400
