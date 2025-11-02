let currentId = null;

async function loadSamples() {
  const resp = await fetch('/tickets/ingest', { method:'POST' });
  await resp.json();
  listTickets();
}

async function listTickets() {
  const resp = await fetch('/tickets');
  const data = await resp.json();
  const div = document.getElementById('tickets');
  div.innerHTML = '';
  data.forEach(t => {
    const c = document.createElement('div'); c.className='card';
    c.innerHTML = `<b>${t.id}</b> — ${t.subject} <span class="badge">${t.priority}</span>
      <div><button onclick="openTicket('${t.id}')">Open</button></div>`;
    div.appendChild(c);
  });
}

async function openTicket(id) {
  currentId = id;
  const resp = await fetch(`/tickets/${id}`);
  const t = await resp.json();
  const d = document.getElementById('detail');
  d.innerHTML = `<div class="card"><b>${t.id}</b><br>${t.subject}<br><pre>${t.description}</pre></div>
    <div class="card"><button onclick="doSummary()">Summarize</button> <button onclick="doTriage()">Triage</button> <button onclick="doSuggest()">Suggest</button></div>
    <div id="out"></div>`;
}

async function doSummary() {
  const resp = await fetch(`/tickets/${currentId}/summary`);
  const r = await resp.json();
  appendOut('Summary', r.summary);
}

async function doTriage() {
  const resp = await fetch(`/tickets/${currentId}/triage`);
  const r = await resp.json();
  appendOut('Triage', JSON.stringify(r, null, 2));
}

async function doSuggest() {
  const resp = await fetch(`/tickets/${currentId}/suggest`);
  const r = await resp.json();
  appendOut('Suggestion', r.suggestion);
}

function appendOut(title, text) {
  const out = document.getElementById('out');
  const c = document.createElement('div'); c.className='card';
  c.innerHTML = `<b>${title}</b><pre>${text}</pre>`;
  out.prepend(c);
}

listTickets();
