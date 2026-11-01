from routing.services.scoring import recommend_route, route_metrics


def _checkpoint(risk, miles):
    return {"risk": risk, "miles_covered": miles}


def test_fewest_severe_miles_wins():
    low_severe = route_metrics([_checkpoint("Severe", 10), _checkpoint("Low", 90)], 100, 3600)
    high_severe = route_metrics([_checkpoint("Severe", 50), _checkpoint("Low", 50)], 100, 3600)
    best = recommend_route([{"metrics": high_severe}, {"metrics": low_severe}])
    assert best == 1


def test_tiebreak_on_high_miles_then_avg_risk_then_duration():
    a = route_metrics([_checkpoint("High", 20), _checkpoint("Low", 80)], 100, 7200)
    b = route_metrics([_checkpoint("High", 5), _checkpoint("Low", 95)], 100, 3600)
    best = recommend_route([{"metrics": a}, {"metrics": b}])
    assert best == 1

    c = route_metrics([_checkpoint("Low", 100)], 100, 7200)
    d = route_metrics([_checkpoint("Low", 100)], 100, 3600)
    best = recommend_route([{"metrics": c}, {"metrics": d}])
    assert best == 1


def test_no_travel_counts_toward_severe_miles():
    with_no_travel = route_metrics([_checkpoint("No Travel", 5), _checkpoint("Low", 95)], 100, 3600)
    all_low = route_metrics([_checkpoint("Low", 100)], 100, 3600)
    best = recommend_route([{"metrics": with_no_travel}, {"metrics": all_low}])
    assert best == 1
