"""Weather risk classification per checkpoint, including load-weight overrides."""

LEVELS = ["Low", "Moderate", "High", "Severe", "No Travel"]
_RANK = {level: i for i, level in enumerate(LEVELS)}

NO_TRAVEL_WIND_MPH = 55
SEVERE_LOAD_OVERRIDE_WIND_MPH = 35
SEVERE_LOAD_OVERRIDE_WIND_MAX_MPH = 44
SEVERE_LOAD_OVERRIDE_LB = 40_000
NO_TRAVEL_LOAD_OVERRIDE_WIND_MPH = 45
NO_TRAVEL_LOAD_OVERRIDE_WIND_MAX_MPH = 54
NO_TRAVEL_LOAD_OVERRIDE_LB = 30_000


def classify_wind(mph):
    if mph < 25:
        return "Low"
    if mph < 35:
        return "Moderate"
    if mph < 45:
        return "High"
    if mph < 55:
        return "Severe"
    return "No Travel"


def classify_rain(in_per_hr):
    if in_per_hr < 0.10:
        return "Low"
    if in_per_hr < 0.25:
        return "Moderate"
    if in_per_hr < 0.50:
        return "High"
    if in_per_hr <= 1.00:
        return "Severe"
    return "No Travel"


def classify_snow(in_per_hr):
    if in_per_hr < 0.5:
        return "Low"
    if in_per_hr < 1.0:
        return "Moderate"
    if in_per_hr < 2.0:
        return "High"
    if in_per_hr <= 3.0:
        return "Severe"
    return "No Travel"


def _apply_load_override(wind_level, wind_mph, load_lb):
    if wind_mph >= NO_TRAVEL_WIND_MPH:
        return "No Travel"
    if NO_TRAVEL_LOAD_OVERRIDE_WIND_MPH <= wind_mph <= NO_TRAVEL_LOAD_OVERRIDE_WIND_MAX_MPH \
            and load_lb > NO_TRAVEL_LOAD_OVERRIDE_LB:
        return "No Travel"
    if SEVERE_LOAD_OVERRIDE_WIND_MPH <= wind_mph <= SEVERE_LOAD_OVERRIDE_WIND_MAX_MPH \
            and load_lb > SEVERE_LOAD_OVERRIDE_LB:
        return "Severe"
    return wind_level


def classify_checkpoint(wind_mph, rain_in_hr, snow_in_hr, load_lb):
    """Return the worst (highest-ranked) risk level across wind, rain, snow,
    with wind subject to load-weight overrides."""
    wind_level = _apply_load_override(classify_wind(wind_mph), wind_mph, load_lb)
    rain_level = classify_rain(rain_in_hr)
    snow_level = classify_snow(snow_in_hr)
    return max([wind_level, rain_level, snow_level], key=lambda level: _RANK[level])
