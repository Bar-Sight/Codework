# BarSight

Real-time bar performance analytics: people counting, inventory tracking, and AI-driven recommendations for bar managers.

## Goal
Build a web-first MVP to demonstrate live people-counting (simulated), POS ingestion (mocked), dashboards, and simple recommendations for pitching and pilot testing.

## Quick start (local)

### Backend (FastAPI)
1. python -m venv venv
2. source venv/bin/activate  # or venv\Scripts\activate on Windows
3. pip install fastapi uvicorn
4. Create app/main.py (see project template)
5. uvicorn app.main:app --reload

### Frontend (React + Vite)
1. npm create vite@latest frontend -- --template react
2. cd frontend && npm install
3. npm run dev

## Core features (MVP)
- Simulated camera events → people counts, gender ratio
- Mock POS ingestion → sales/events
- Dashboard: live metrics, charts, inventory snapshot
- Basic recommendations: low-stock alerts, peak-hour suggestions
- Demo mode with prerecorded/simulated scenarios

## Tech choices (initial)
- Backend: FastAPI (Python)
- Frontend: React + Vite
- DB: Postgres (or simple local JSON for prototype)
- Mocking: Python scripts (OpenCV later for camera simulation)
- Charting: Chart.js / Recharts

## 12-week roadmap (short)
- Weeks 1–2: Spec, data model, wireframes
- Weeks 3–4: Backend skeleton, mock data pipeline
- Weeks 5–6: Frontend dashboard + auth
- Weeks 7–8: Simple analytics & recommendations
- Week 9: Camera/edge prototype integration (simulated)
- Week 10: Polish & onboarding flows
- Week 11: User testing & iterate
- Week 12: Final demo, pitch deck, deploy

## Project structure (suggested)
- /app — FastAPI backend
  - main.py
  - routes/
  - models/
  - services/
- /frontend — React app (Vite)
- /scripts — mock data generator, demo scripts
- /docs — design, roadmap, pitch deck
- README.md
- .env.example

## License
MIT

## Contact
Project leads: Marcos Cortez and Luca Daste — marcos.a.cortez@outlook.com - lucadaste5@gmail.com
