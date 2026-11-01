"""Sample checkpoints along a route geometry at a mileage interval, with ETAs."""

import math
from datetime import timedelta

METERS_PER_MILE = 1609.344


def checkpoint_interval_miles(total_miles):
    """Spec: sample every 10/25/50 miles depending on route length, so short trips
    get fine-grained sampling and long trips don't produce excessive checkpoints."""
    if total_miles <= 100:
        return 10
    if total_miles <= 300:
        return 25
    return 50


def _haversine_miles(p1, p2):
    lon1, lat1 = p1
    lon2, lat2 = p2
    r = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def sample_checkpoints(geometry, distance_m, duration_s, departure_dt):
    """geometry: list of [lon, lat]. Returns checkpoints at the chosen mile interval,
    each with coords, cumulative miles, eta, and miles_covered (this checkpoint's
    share of the route for risk-weighted mileage totals)."""
    total_miles = distance_m / METERS_PER_MILE
    interval = checkpoint_interval_miles(total_miles)

    segment_miles = [0.0]
    for i in range(1, len(geometry)):
        segment_miles.append(segment_miles[-1] + _haversine_miles(geometry[i - 1], geometry[i]))
    route_length = segment_miles[-1] or 1e-9

    targets = list(range(0, int(total_miles), interval)) + [total_miles]
    targets = sorted(set(round(t, 2) for t in targets))

    checkpoints = []
    geom_idx = 0
    prev_target = 0
    for target in targets:
        while geom_idx < len(segment_miles) - 1 and segment_miles[geom_idx + 1] < target:
            geom_idx += 1
        lon, lat = geometry[min(geom_idx, len(geometry) - 1)]
        fraction = min(target / route_length, 1.0)
        eta_seconds = fraction * duration_s
        checkpoints.append({
            "lon": lon,
            "lat": lat,
            "distance_miles": round(target, 1),
            "miles_covered": round(target - prev_target, 1),
            "eta": departure_dt + timedelta(seconds=eta_seconds),
        })
        prev_target = target

    return checkpoints, interval
