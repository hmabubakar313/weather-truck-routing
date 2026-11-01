"""Route recommendation: rank routes by severe miles, high miles, avg risk, then duration."""

from .risk import _RANK


def _risk_score(level):
    return _RANK[level]


def route_metrics(checkpoints, segment_miles, duration_seconds):
    """checkpoints: list of dicts with 'risk' and 'miles_covered' (miles this checkpoint represents)."""
    severe_miles = sum(c["miles_covered"] for c in checkpoints if c["risk"] in ("Severe", "No Travel"))
    high_miles = sum(c["miles_covered"] for c in checkpoints if c["risk"] == "High")
    avg_risk = (
        sum(_risk_score(c["risk"]) for c in checkpoints) / len(checkpoints)
        if checkpoints else 0
    )
    return {
        "severe_miles": round(severe_miles, 1),
        "high_miles": round(high_miles, 1),
        "avg_risk_score": round(avg_risk, 2),
        "duration_seconds": duration_seconds,
    }


def ranking_key(metrics):
    return (metrics["severe_miles"], metrics["high_miles"], metrics["avg_risk_score"], metrics["duration_seconds"])


def recommend_route(routes):
    """routes: list of dicts each with a 'metrics' key (from route_metrics).
    Returns the index of the recommended route."""
    return min(range(len(routes)), key=lambda i: ranking_key(routes[i]["metrics"]))
