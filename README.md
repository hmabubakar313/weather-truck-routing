# Weather-Aware Truck Routing

React + Django app that recommends the safest truck route between an origin and
destination, factoring in weather risk (wind/rain/snow) and load weight, with
checkpoints sampled along the route at arrival-time-based intervals and a 0-48h
weather heatmap slider.

## Stack

- **Backend**: Django + Django REST Framework, stateless (no DB models beyond Django's
  own internal tables).
- **Frontend**: React (Vite) + react-leaflet (OpenStreetMap tiles, no API key).
- **Routing/geocoding**: [OpenRouteService](https://openrouteservice.org/dev/#/signup)
  (free tier, requires a free API key).
- **Weather**: [Open-Meteo](https://open-meteo.com/) (free, no API key required).

## Risk logic (backend/routing/services)

- `risk.py` — classifies wind/rain/snow per the assessment's threshold table, takes
  the worst of the three per checkpoint, and applies the load-weight overrides
  (≥55 mph → No Travel; 45-54 mph + >30,000 lb → No Travel; 35-44 mph + >40,000 lb →
  Severe).
- `scoring.py` — ranks routes by (fewest severe miles, fewest high miles, lowest
  average risk score, shortest duration), in that order.
- `geometry.py` — samples checkpoints along the route geometry at 10/25/50-mile
  intervals depending on total trip length, computing each checkpoint's ETA from the
  departure time and cumulative route duration.
- `heatmap.py` — pre-fetches a 48-hour forecast per checkpoint on the recommended
  route so the frontend's hour slider (0-48h) doesn't trigger new API calls.

Covered by unit tests in `backend/routing/tests/` (36 pure-logic tests + a mocked
end-to-end API test).

## Local development

### Backend

```bash
cd backend
python3.12 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then set ORS_API_KEY
python manage.py migrate
python manage.py runserver
```

Run tests:

```bash
source venv/bin/activate
python -m pytest routing/tests -q
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env   # VITE_API_BASE_URL, defaults to http://localhost:8000
npm run dev
```

Open http://localhost:5173.

## Docker

```bash
cp backend/.env.example backend/.env   # then set ORS_API_KEY
docker compose up --build
```

- Backend: http://localhost:8000
- Frontend: http://localhost:3000

Both services have been verified to build and run together via
`docker compose up --build` (confirmed with `curl` against `/api/routes/` and the
frontend root).

## Getting an OpenRouteService API key

This project requires a free ORS API key to call routing/geocoding. Sign up at
https://openrouteservice.org/dev/#/signup (no credit card), create a token, and set
it as `ORS_API_KEY` in `backend/.env` (or as a Render environment variable).

**Note**: no live ORS key was available while building this repo in this environment,
so the routing/geocoding → weather → risk → recommendation pipeline was verified via:
1. 36 unit tests covering every risk threshold boundary and load-rule override, and
   the route-ranking tie-break order.
2. A mocked end-to-end test of `POST /api/routes/` (`test_plan_routes_returns_recommendation`)
   that exercises the full view with fake ORS/Open-Meteo responses.
3. A live `docker compose` run confirming both containers start, talk to each other,
   and the backend correctly surfaces a clean error when given an invalid ORS key
   (502 with a readable message) rather than crashing.

Once a real `ORS_API_KEY` is set, the same code path runs against live routing and
weather data with no changes required — this should be the first thing verified
after pulling the repo.

## Deployment (Render, free tier)

`render.yaml` defines two Docker-based web services (backend, frontend). To deploy:

1. Push this repo to GitHub.
2. In Render, choose "New > Blueprint" and point it at the repo — it will read
   `render.yaml` and create both services.
3. Set the `ORS_API_KEY` environment variable on the backend service (marked
   `sync: false` in `render.yaml`, so Render will prompt for it).
4. After the backend deploys, update `CORS_ALLOWED_ORIGINS` on the backend and
   `VITE_API_BASE_URL` build arg on the frontend to match the actual `*.onrender.com`
   URLs Render assigns (the placeholders in `render.yaml` assume default service
   names).

Render's free web services spin down after inactivity and cold-start on the next
request (~30-60s) — acceptable for an assessment demo, mention this in the Loom
walkthrough if the first request is slow.

## Requirements checklist (vs. the assessment PDF)

- [x] Origin, destination, departure date/time, load weight inputs
- [x] 3 route options via a routing API (ORS `alternative_routes`)
- [x] Checkpoints sampled every 10/25/50 mi depending on trip length, using arrival
      time at each checkpoint (not departure time) for the weather lookup
- [x] Risk classified per the wind/rain/snow thresholds, worst-of-three per checkpoint
- [x] Load-weight override rules applied
- [x] Route recommendation ranked by fewest severe miles → fewest high miles →
      lowest avg risk → shortest duration
- [x] Map shows all routes, checkpoints, risk levels (color-coded), ETAs (in
      checkpoint popups), and route summaries (distance/duration/severe-high
      miles/avg risk) in the sidebar
- [x] Weather heatmap along the corridor with a 0-48h slider
- [x] Dockerized, `docker-compose.yml`, `.env.example` for both services
- [x] Free deployment path documented (Render)
- [ ] Not verified against live routing/weather data (no ORS key available in this
      environment) — unit/mocked tests pass; needs a real key for final sign-off

## Deliverables still owed by the person submitting this assessment

- A real `ORS_API_KEY` (sign up, confirm the pipeline works live, then commit nothing
  secret — the key only goes in `.env` / Render's dashboard).
- Push to GitHub and deploy via Render as above.
- Record the 5-10 min Loom walkthrough (not something that can be produced here).
