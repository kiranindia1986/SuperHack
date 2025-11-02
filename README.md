# Technician Copilot — MVP (FastAPI)

AI-powered *Technician Copilot* MVP for MSP/IT teams: ticket summarization, smart triage, knowledge suggestions, time/SLA signals and a tiny web UI.

**Why this repo?** Designed for hackathons: runs locally, no external keys required. If you set `OPENAI_API_KEY`, the LLM-powered paths will be used; otherwise, heuristic fallbacks run.

## Features (MVP)
- POST `/tickets/ingest` — ingest a ticket (or load sample data)
- GET `/tickets` — list tickets
- GET `/tickets/{id}/summary` — 3-bullet summary (LLM or heuristic)
- GET `/tickets/{id}/triage` — resolver group + confidence
- GET `/tickets/{id}/suggest` — 1–3 steps using KB search
- GET `/metrics` — demo SLA/time metrics
- Simple web UI at `/` (static HTML + fetch)

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# (Optional) export OPENAI_API_KEY=sk-...

uvicorn app.main:app --reload
# open http://127.0.0.1:8000
```

## Project layout
```
app/
  main.py           # API + static web
  kb_search.py      # TF-IDF vector search over /app/kb/*.md
  triage.py         # keyword-based resolver suggestion (fallback)
  llm.py            # LLM calls (OpenAI) + heuristic summary/suggest
  static/
    index.html      # minimal UI
    js/app.js
data/
  sample_tickets.json
requirements.txt
```

## KB content
Edit/add markdown files in `app/kb/`. Rebuild index automatically on server start.

## Benchmarks (quick demo)
`/metrics` computes rough admin-time-saved and SLA risk for visible effect during demo.

## License
MIT
