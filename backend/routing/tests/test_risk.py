import pytest

from routing.services.risk import classify_checkpoint, classify_rain, classify_snow, classify_wind


@pytest.mark.parametrize("mph,expected", [
    (0, "Low"), (24.9, "Low"),
    (25, "Moderate"), (34.9, "Moderate"),
    (35, "High"), (44.9, "High"),
    (45, "Severe"), (54.9, "Severe"),
    (55, "No Travel"), (100, "No Travel"),
])
def test_classify_wind(mph, expected):
    assert classify_wind(mph) == expected


@pytest.mark.parametrize("rate,expected", [
    (0, "Low"), (0.09, "Low"),
    (0.10, "Moderate"), (0.24, "Moderate"),
    (0.25, "High"), (0.49, "High"),
    (0.50, "Severe"), (1.00, "Severe"),
    (1.01, "No Travel"),
])
def test_classify_rain(rate, expected):
    assert classify_rain(rate) == expected


@pytest.mark.parametrize("rate,expected", [
    (0, "Low"), (0.49, "Low"),
    (0.5, "Moderate"), (0.99, "Moderate"),
    (1.0, "High"), (1.99, "High"),
    (2.0, "Severe"), (3.0, "Severe"),
    (3.01, "No Travel"),
])
def test_classify_snow(rate, expected):
    assert classify_snow(rate) == expected


def test_no_travel_wind_overrides_any_load():
    assert classify_checkpoint(wind_mph=55, rain_in_hr=0, snow_in_hr=0, load_lb=1) == "No Travel"
    assert classify_checkpoint(wind_mph=60, rain_in_hr=0, snow_in_hr=0, load_lb=50_000) == "No Travel"


def test_heavy_load_forces_no_travel_in_45_to_54_band():
    assert classify_checkpoint(wind_mph=50, rain_in_hr=0, snow_in_hr=0, load_lb=30_001) == "No Travel"
    # at or below 30,000 lb, stays Severe (no override)
    assert classify_checkpoint(wind_mph=50, rain_in_hr=0, snow_in_hr=0, load_lb=30_000) == "Severe"


def test_heavy_load_forces_severe_in_35_to_44_band():
    assert classify_checkpoint(wind_mph=40, rain_in_hr=0, snow_in_hr=0, load_lb=40_001) == "Severe"
    # at or below 40,000 lb, stays High (no override)
    assert classify_checkpoint(wind_mph=40, rain_in_hr=0, snow_in_hr=0, load_lb=40_000) == "High"


def test_checkpoint_takes_worst_of_wind_rain_snow():
    assert classify_checkpoint(wind_mph=0, rain_in_hr=0.6, snow_in_hr=0, load_lb=1000) == "Severe"
    assert classify_checkpoint(wind_mph=0, rain_in_hr=0, snow_in_hr=3.5, load_lb=1000) == "No Travel"


def test_light_load_no_override():
    assert classify_checkpoint(wind_mph=40, rain_in_hr=0, snow_in_hr=0, load_lb=5000) == "High"
    assert classify_checkpoint(wind_mph=50, rain_in_hr=0, snow_in_hr=0, load_lb=5000) == "Severe"
