from typing import Dict, Tuple
import re

GROUPS = {
    'Print-Services': ['printer', 'print', 'spooler', 'driver', 'tray', 'toner'],
    'Network': ['vpn', 'latency', 'dns', 'network', 'wifi', 'switch', 'router'],
    'Windows-Desktop': ['windows', 'bsod', 'update', 'policy', 'gpo', 'login'],
    'Email': ['outlook', 'exchange', 'mail', 'smtp', 'imap'],
    'SaaS-Apps': ['salesforce', 'crm', 'zoom', 'teams', 'slack', 'okta', 'sso'],
}

def suggest_group(text: str) -> Tuple[str, float, str]:
    t = text.lower()
    best, best_score = 'Other', 0.0
    for group, kws in GROUPS.items():
        score = sum(1 for kw in kws if re.search(r'\b' + re.escape(kw) + r'\b', t))
        if score > best_score:
            best, best_score = group, score
    conf = min(1.0, 0.2 + 0.2 * best_score) if best_score else 0.25
    rationale = f"Matched keywords: {best_score}" if best_score else "No strong keywords; defaulting to Other"
    return best, conf, rationale
