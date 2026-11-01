from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import RouteRequestSerializer
from .services import ors, scoring
from .services.geometry import sample_checkpoints
from .services.heatmap import build_corridor_heatmap
from .services.risk import classify_checkpoint
from .services.weather import fetch_hourly_forecast_many, forecast_days_for, weather_at


def _build_route(raw_route, departure_dt, load_lb):
    checkpoints, interval_miles = sample_checkpoints(
        raw_route["geometry"], raw_route["distance_m"], raw_route["duration_s"], departure_dt,
    )
    # cover the whole trip duration plus the heatmap's 48h lookahead past departure
    extra_hours = max(48, raw_route["duration_s"] / 3600)
    forecast_days = forecast_days_for(departure_dt, extra_hours=extra_hours)
    hourly_blocks = fetch_hourly_forecast_many(
        [(cp["lat"], cp["lon"]) for cp in checkpoints], forecast_days=forecast_days,
    )
    for cp, hourly in zip(checkpoints, hourly_blocks):
        weather = weather_at(hourly, cp["eta"])
        cp["weather"] = weather
        cp["risk"] = classify_checkpoint(weather["wind_mph"], weather["rain_in_hr"], weather["snow_in_hr"], load_lb)
        cp["eta"] = cp["eta"].isoformat()

    metrics = scoring.route_metrics(checkpoints, raw_route["distance_m"], raw_route["duration_s"])
    return {
        "checkpoints": checkpoints,
        "checkpoint_interval_miles": interval_miles,
        "geometry": raw_route["geometry"],
        "distance_miles": round(raw_route["distance_m"] / 1609.344, 1),
        "duration_seconds": raw_route["duration_s"],
        "metrics": metrics,
    }


@api_view(["POST"])
def plan_routes(request):
    serializer = RouteRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    try:
        origin_coords = ors.geocode(data["origin"])
        destination_coords = ors.geocode(data["destination"])
        raw_routes = ors.get_routes(origin_coords, destination_coords)
    except ors.ORSError as exc:
        return Response({"error": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

    if not raw_routes:
        return Response({"error": "no routes found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        routes = [_build_route(r, data["departure_time"], data["load_weight_lb"]) for r in raw_routes]
    except Exception as exc:  # weather provider failure
        return Response({"error": f"weather lookup failed: {exc}"}, status=status.HTTP_502_BAD_GATEWAY)

    recommended_index = scoring.recommend_route(routes)

    corridor_checkpoints = routes[recommended_index]["checkpoints"]
    try:
        heatmap = build_corridor_heatmap(corridor_checkpoints, data["departure_time"], data["load_weight_lb"])
    except Exception:
        heatmap = []

    return Response({
        "origin": {"lon": origin_coords[0], "lat": origin_coords[1]},
        "destination": {"lon": destination_coords[0], "lat": destination_coords[1]},
        "routes": routes,
        "recommended_index": recommended_index,
        "heatmap": heatmap,
    })
