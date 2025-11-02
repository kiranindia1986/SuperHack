import os
from typing import List, Dict
from openai import OpenAI

def use_openai() -> bool:
    return bool(os.getenv('OPENAI_API_KEY'))

def summarize_heuristic(text: str) -> str:
    parts = [p.strip() for p in text.replace('\n', ' ').split('.') if p.strip()]
    problem = parts[0] if parts else text[:120]
    suspected = next((p for p in parts[1:4] if len(p) > 20), 'Possible driver or config issue.')
    action = 'Check KB suggestions and attempt first remediation step.'
    return f"• Problem: {problem}.\n• Suspected cause: {suspected}.\n• First action: {action}"

def summarize_openai(text: str) -> str:
    client = OpenAI()
    prompt = f"Summarize in 3 bullets: (1) problem (2) suspected cause (3) first action. Max 60 words.\nTEXT:\n{text}"
    resp = client.chat.completions.create(model="gpt-4o-mini", messages=[
        {"role":"system","content":"You are a precise IT service desk assistant."},
        {"role":"user","content":prompt}
    ])
    return resp.choices[0].message.content.strip()

def suggest_from_snippets(text: str, snippets: List[Dict]) -> str:
    if not snippets:
        return "No relevant KB found. Try standard checks: restart service, update driver, verify access."
    steps = []
    for sn in snippets[:3]:
        lines = [l.strip('- ') for l in sn['snippet'].splitlines() if l.strip()]
        items = [l for l in lines if l[:2].isdigit() or l.startswith(('1.', '2.', '3.'))]
        if items:
            steps.append(f"From {sn['title']}: " + ' '.join(items[:2]))
    if not steps:
        steps = [f"Review KB: {snippets[0]['title']} and apply first 2 steps."]
    return '\n'.join(f"• {s}" for s in steps[:3])
