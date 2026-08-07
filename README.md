# AutoOps - Unified Multi-Agent Platform (Day 1 skeleton)

## Structure
```
backend/    FastAPI app (uvicorn)
agents/     LangGraph agent pipeline (skeleton in graph.py)
frontend/   Next.js app
docs/       shared schema + policy rules
docker-compose.yml   local Postgres + Redis
.env.example          copy to .env and fill in API keys
```

## Setup (see chat for full walkthrough)

1. `cp .env.example .env` and fill in GEMINI_API_KEY / GROQ_API_KEY / DATABASE_URL
2. Backend: `cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
3. Run backend: `uvicorn app.main:app --reload --port 8000` (from inside `backend/`)
4. Frontend: `cd frontend && npm install && npm run dev`
5. Infra: `docker compose up -d` (starts Postgres + Redis)
6. Agent skeleton: `python agents/graph.py` (from repo root, with venv active)
