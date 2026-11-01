"""OpenRouteService client: geocoding + truck/driving directions with alternatives."""

import os

import httpx

ORS_BASE_URL = "https://api.openrouteservice.org"


class ORSError(Exception):
    pass


def _api_key():
    key = os.environ.get("ORS_API_KEY")
    if not key:
        raise ORSError("ORS_API_KEY is not set")
    return key


def _get(url, params):
    try:
        return httpx.get(url, params=params, timeout=15)
    except httpx.HTTPError as exc:
        raise ORSError(f"could not reach OpenRouteService: {exc}") from exc


def _post(url, params, json_body, timeout):
    try:
        return httpx.post(url, params=params, json=json_body, timeout=timeout)
    except httpx.HTTPError as exc:
        raise ORSError(f"could not reach OpenRouteService: {exc}") from exc


def geocode(query):
    """Return (lon, lat) for a free-text place query."""
    resp = _get(f"{ORS_BASE_URL}/geocode/search", {"api_key": _api_key(), "text": query, "size": 1})
    if resp.status_code != 200:
        raise ORSError(f"geocoding failed for {query!r}: {resp.status_code} {resp.text}")
    features = resp.json().get("features", [])
    if not features:
        raise ORSError(f"no geocoding match for {query!r}")
    lon, lat = features[0]["geometry"]["coordinates"]
    return lon, lat


ALTERNATIVE_ROUTES_MAX_METERS = 100_000
FALLBACK_PREFERENCES = ["fastest", "shortest", "recommended"]
# "recommended" often matches "fastest" on corridors with one practical highway;
# these force a genuinely different path when that happens.
EXTRA_FALLBACK_REQUESTS = [
    {"preference": "fastest", "options": {"avoid_features": ["highways"]}},
    {"preference": "shortest", "options": {"avoid_features": ["tollways"]}},
    {"preference": "fastest", "options": {"avoid_features": ["tollways"]}},
]


def _feature_to_route(feature):
    summary = feature["properties"]["summary"]
    return {
        "geometry": feature["geometry"]["coordinates"],
        "distance_m": summary["distance"],
        "duration_s": summary["duration"],
    }


def _directions_request(origin_coords, destination_coords, extra_body):
    body = {
        "coordinates": [list(origin_coords), list(destination_coords)],
        "instructions": False,
        **extra_body,
    }
    return _post(f"{ORS_BASE_URL}/v2/directions/driving-hgv/geojson", {"api_key": _api_key()}, body, timeout=30)


def _is_alternative_routes_too_long_error(resp):
    if resp.status_code != 400:
        return False
    try:
        return resp.json().get("error", {}).get("code") == 2004
    except ValueError:
        return False


def _try_add_route(origin_coords, destination_coords, body, routes, seen):
    resp = _directions_request(origin_coords, destination_coords, body)
    if resp.status_code != 200:
        return
    feature = resp.json()["features"][0]
    route = _feature_to_route(feature)
    key = (round(route["distance_m"]), round(route["duration_s"]))
    if key in seen:
        return
    seen.add(key)
    routes.append(route)


def _get_routes_by_preference(origin_coords, destination_coords, count):
    """Fallback for trips over ORS's 100km alternative-routes limit: request one
    route per preference so we still get genuinely different paths. If preferences
    collapse to the same path (common on corridors with one practical highway),
    force distinct routes by avoiding highways/tollways instead."""
    routes = []
    seen = set()
    for preference in FALLBACK_PREFERENCES[:count]:
        _try_add_route(origin_coords, destination_coords, {"preference": preference}, routes, seen)
    for extra in EXTRA_FALLBACK_REQUESTS:
        if len(routes) >= count:
            break
        _try_add_route(origin_coords, destination_coords, extra, routes, seen)
    if not routes:
        raise ORSError("routing failed: no routes available for this trip")
    return routes


def get_routes(origin_coords, destination_coords, alternatives=3):
    """origin_coords/destination_coords: (lon, lat) tuples.
    Returns a list of routes, each {"geometry": [[lon, lat], ...], "distance_m": float, "duration_s": float}."""
    resp = _directions_request(origin_coords, destination_coords, {
        "alternative_routes": {"target_count": alternatives, "share_factor": 0.6, "weight_factor": 1.6},
    })
    if _is_alternative_routes_too_long_error(resp):
        return _get_routes_by_preference(origin_coords, destination_coords, alternatives)
    if resp.status_code != 200:
        raise ORSError(f"routing failed: {resp.status_code} {resp.text}")
    return [_feature_to_route(f) for f in resp.json().get("features", [])]
