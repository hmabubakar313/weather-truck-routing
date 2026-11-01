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

