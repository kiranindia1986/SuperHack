import os, json, datetime as dt
from pathlib import Path
from typing import Dict, Any, List
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from .kb_search import KBSearch
from .triage import suggest_group
from .llm import use_openai, summarize_openai, summarize_heuristic, suggest_from_snippets

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / 'data' / 'sample_tickets.json'

app = FastAPI(title="Technician Copilot — MVP", version="0.1.0")
app.mount("/static", StaticFiles(directory=str(BASE / 'app' / 'static')), name="static")

# in-memory store
TICKETS: Dict[str, Dict[str, Any]] = {}
TIME_EVENTS: List[Dict[str, Any]] = []

kb = KBSearch(str(BASE / 'app' / 'kb'))

class Ticket(BaseModel):
    id: str
    subject: str
    description: str
    priority: str = 'Low'
    category: str = 'Other'
    requester: str = 'user@example.com'
    created_at: str = dt.datetime.utcnow().isoformat()+'Z'

def set_sla_due(ticket: Dict[str, Any], hours: int = 4):
    created = dt.datetime.fromisoformat(ticket['created_at'].replace('Z',''))
    ticket['sla_due'] = (created + dt.timedelta(hours=hours)).isoformat()+'Z'

@app.get("/", response_class=HTMLResponse)
def index():
    return (BASE / 'app' / 'static' / 'index.html').read_text()

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/tickets/ingest")
def ingest_samples():
    items = json.loads(DATA.read_text())
    for t in items:
        TICKETS[t['id']] = t
        set_sla_due(TICKETS[t['id']], hours=4)
    return {"loaded": len(items)}

@app.get("/tickets")
def list_tickets():
    return list(TICKETS.values())

@app.post("/tickets")
def create_ticket(t: Ticket):
    TICKETS[t.id] = t.dict()
    set_sla_due(TICKETS[t.id], hours=4)
    return {"ok": True}

@app.get("/tickets/{id}")
def get_ticket(id: str):
    return TICKETS[id]

@app.get("/tickets/{id}/summary")
def ticket_summary(id: str):
    t = TICKETS[id]
    text = f"{t['subject']}. {t['description']}"
    summary = summarize_openai(text) if use_openai() else summarize_heuristic(text)
    TIME_EVENTS.append({"ticket_id": id, "event": "copilot_summary", "minutes": 2, "ts": dt.datetime.utcnow().isoformat()+"Z"})
    return {"summary": summary}

@app.get("/tickets/{id}/triage")
def ticket_triage(id: str):
    t = TICKETS[id]
    text = f"{t['subject']}\n{t['description']}"
    group, conf, rationale = suggest_group(text)
    TIME_EVENTS.append({"ticket_id": id, "event": "copilot_triage", "minutes": 2, "ts": dt.datetime.utcnow().isoformat()+"Z"})
    return {"resolver_group": group, "confidence": conf, "rationale": rationale}

@app.get("/tickets/{id}/suggest")
def ticket_suggest(id: str):
    t = TICKETS[id]
    query = f"{t['subject']} {t['description']}"
    hits = kb.search(query, k=3)
    suggestion = suggest_from_snippets(query, hits)
    TIME_EVENTS.append({"ticket_id": id, "event": "copilot_suggest", "minutes": 1, "ts": dt.datetime.utcnow().isoformat()+"Z"})
    return {"hits": hits, "suggestion": suggestion}

@app.get("/metrics")
def metrics():
    admin_time_saved = sum(ev['minutes'] for ev in TIME_EVENTS)
    now = dt.datetime.utcnow()
    sla_risk = sum(1 for t in TICKETS.values()
                   if (now + dt.timedelta(minutes=30)) > dt.datetime.fromisoformat(t['sla_due'].replace('Z','')))
    return {"admin_time_saved_minutes": admin_time_saved, "sla_at_risk": sla_risk, "events": TIME_EVENTS[-10:]}
