"""WarderBox Web Dashboard — real-time monitoring with zero dependencies.

Serves a single-page dashboard that shows:
- Live action stats (total, blocked, errors, cost)
- Recent action log
- Budget status
- Rate limit stats

Uses Python's built-in http.server. No external packages needed.

Usage:
    from warderbox.dashboard import start_dashboard

    shield = WarderBox(budget=10.0, db_path="audit.db")
    # ... register tools, do work ...

    start_dashboard(shield, port=8080)
    # Open http://localhost:8080
"""

from __future__ import annotations

import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from warderbox.shield import WarderBox

_DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>WarderBox Dashboard</title>
<style>
:root {
  --bg: #0f172a; --surface: #1e293b; --border: #334155;
  --text: #f1f5f9; --muted: #94a3b8; --accent: #3b82f6;
  --green: #22c55e; --red: #ef4444; --yellow: #eab308; --orange: #f97316;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: var(--bg); color: var(--text); min-height: 100vh; }
.header { background: var(--surface); border-bottom: 1px solid var(--border);
  padding: 16px 24px; display: flex; align-items: center; gap: 12px; }
.header h1 { font-size: 20px; font-weight: 600; }
.header .badge { background: var(--accent); color: white; padding: 2px 8px;
  border-radius: 12px; font-size: 12px; font-weight: 500; }
.container { max-width: 1200px; margin: 0 auto; padding: 24px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px; margin-bottom: 24px; }
.card { background: var(--surface); border: 1px solid var(--border);
  border-radius: 12px; padding: 20px; }
.card h3 { font-size: 13px; color: var(--muted); text-transform: uppercase;
  letter-spacing: 0.5px; margin-bottom: 8px; }
.card .value { font-size: 32px; font-weight: 700; }
.card .sub { font-size: 13px; color: var(--muted); margin-top: 4px; }
.green { color: var(--green); }
.red { color: var(--red); }
.yellow { color: var(--yellow); }
.orange { color: var(--orange); }
.table-card { background: var(--surface); border: 1px solid var(--border);
  border-radius: 12px; overflow: hidden; }
.table-card h2 { padding: 16px 20px; font-size: 16px; border-bottom: 1px solid var(--border); }
table { width: 100%; border-collapse: collapse; }
th { text-align: left; padding: 10px 20px; font-size: 12px; color: var(--muted);
  text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid var(--border); }
td { padding: 10px 20px; font-size: 14px; border-bottom: 1px solid var(--border); }
tr:last-child td { border-bottom: none; }
.status { padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 500; }
.status-ok { background: #166534; color: #86efac; }
.status-blocked { background: #991b1b; color: #fca5a5; }
.status-error { background: #92400e; color: #fde68a; }
.budget-bar { height: 8px; background: var(--border); border-radius: 4px;
  margin-top: 12px; overflow: hidden; }
.budget-fill { height: 100%; border-radius: 4px; transition: width 0.5s; }
.auto-refresh { font-size: 12px; color: var(--muted); }
</style>
</head>
<body>
<div class="header">
  <h1>WarderBox</h1>
  <span class="badge">LIVE</span>
  <span class="auto-refresh">Auto-refresh: 3s</span>
</div>
<div class="container">
  <div class="grid" id="stats"></div>
  <div class="grid">
    <div class="card" id="budget-card"></div>
    <div class="card" id="rate-card"></div>
  </div>
  <div class="table-card">
    <h2>Recent Actions</h2>
    <table><thead><tr>
      <th>Tool</th><th>Risk</th><th>Status</th><th>Cost</th><th>Time</th>
    </tr></thead><tbody id="log-body"></tbody></table>
  </div>
</div>
<script>
async function refresh() {
  try {
    const r = await fetch('/api/stats');
    const d = await r.json();
    document.getElementById('stats').innerHTML = `
      <div class="card"><h3>Total Actions</h3>
        <div class="value">${d.total_actions}</div></div>
      <div class="card"><h3>Successful</h3>
        <div class="value green">${d.successful}</div></div>
      <div class="card"><h3>Blocked</h3>
        <div class="value red">${d.blocked}</div></div>
      <div class="card"><h3>Errors</h3>
        <div class="value orange">${d.errors}</div></div>`;
    const b = d.budget;
    const pct = b.budget ? Math.min(100, (b.spent / b.budget) * 100) : 0;
    const bcolor = pct > 80 ? 'var(--red)' : pct > 50 ? 'var(--yellow)' : 'var(--green)';
    document.getElementById('budget-card').innerHTML = `
      <h3>Budget</h3>
      <div class="value">$${b.spent.toFixed(2)}</div>
      <div class="sub">${b.budget ? 'of $' + b.budget.toFixed(2) + ' (' + pct.toFixed(0) + '%)' : 'No limit set'}</div>
      ${b.budget ? '<div class="budget-bar"><div class="budget-fill" style="width:'+pct+'%;background:'+bcolor+'"></div></div>' : ''}`;
    const rl = d.rate_limits;
    document.getElementById('rate-card').innerHTML = `
      <h3>Rate Limits</h3>
      <div class="value">${rl.global_last_minute}</div>
      <div class="sub">${rl.global_last_minute} calls/min | ${rl.global_last_hour} calls/hr</div>`;
  } catch(e) {}
  try {
    const r = await fetch('/api/history');
    const rows = await r.json();
    const tbody = document.getElementById('log-body');
    tbody.innerHTML = rows.slice(-50).reverse().map(h => {
      const status = h.blocked ? 'blocked' : (h.success ? 'ok' : 'error');
      const label = h.blocked ? 'BLOCKED' : (h.success ? 'OK' : 'ERROR');
      const t = new Date(h.timestamp * 1000).toLocaleTimeString();
      return `<tr><td>${h.tool}</td><td>${h.risk.toUpperCase()}</td>
        <td><span class="status status-${status}">${label}</span></td>
        <td>$${h.cost.toFixed(2)}</td><td>${t}</td></tr>`;
    }).join('');
  } catch(e) {}
}
refresh();
setInterval(refresh, 3000);
</script>
</body>
</html>"""


class _DashboardHandler(BaseHTTPRequestHandler):
    shield: WarderBox

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self._respond(200, "text/html", _DASHBOARD_HTML)
        elif self.path == "/api/stats":
            data = self.shield.stats()
            self._respond(200, "application/json", json.dumps(data))
        elif self.path == "/api/history":
            data = self.shield.history()
            self._respond(200, "application/json", json.dumps(data))
        else:
            self._respond(404, "text/plain", "Not found")

    def _respond(self, code: int, content_type: str, body: str):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def log_message(self, format, *args):
        pass


def start_dashboard(
    shield: WarderBox,
    port: int = 8080,
    host: str = "127.0.0.1",
    open_browser: bool = True,
    background: bool = True,
) -> HTTPServer:
    """Start the WarderBox web dashboard.

    Args:
        shield: The WarderBox instance to monitor.
        port: Port to serve on (default 8080).
        host: Host to bind to (default localhost).
        open_browser: Open the dashboard in the default browser.
        background: Run in a background thread (default True).

    Returns:
        The HTTPServer instance (call .shutdown() to stop).
    """
    handler = type("Handler", (_DashboardHandler,), {"shield": shield})
    server = HTTPServer((host, port), handler)

    if background:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
    else:
        if open_browser:
            import webbrowser
            webbrowser.open(f"http://{host}:{port}")
        server.serve_forever()
        return server

    if open_browser:
        import webbrowser
        webbrowser.open(f"http://{host}:{port}")

    return server
