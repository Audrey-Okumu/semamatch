from flask import Blueprint, jsonify, Response
from app.models.caller import Caller

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def health_check():
    return jsonify({"status": "SemaMatch backend is running"})


@dashboard_bp.route("/api/callers")
def list_callers():
    callers = Caller.query.order_by(Caller.created_at.desc()).all()
    return jsonify([c.to_dict() for c in callers])


@dashboard_bp.route("/dashboard")
def dashboard():
    return Response(DASHBOARD_HTML, mimetype="text/html")


DASHBOARD_HTML = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>SemaMatch — Live Queue</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
    background: radial-gradient(1200px 600px at 20% -10%, #1c2145 0%, #0d0f1f 55%);
    color: #e9ecff; min-height: 100vh; padding: 28px;
  }
  .top { display: flex; align-items: center; gap: 14px; margin-bottom: 6px; }
  .live { display: inline-flex; align-items: center; gap: 7px; font-size: 12px;
    letter-spacing: .12em; color: #7ef0c2; text-transform: uppercase; }
  .dot { width: 9px; height: 9px; border-radius: 50%; background: #35e39a;
    box-shadow: 0 0 0 0 rgba(53,227,154,.7); animation: pulse 1.6s infinite; }
  @keyframes pulse { 0%{box-shadow:0 0 0 0 rgba(53,227,154,.6)}
    70%{box-shadow:0 0 0 10px rgba(53,227,154,0)} 100%{box-shadow:0 0 0 0 rgba(53,227,154,0)} }
  h1 { font-size: 26px; font-weight: 700; }
  .tag-line { color: #9aa0c9; font-size: 14px; margin-bottom: 22px; }
  .stats { display: flex; gap: 14px; margin-bottom: 26px; flex-wrap: wrap; }
  .stat { background: #161a34; border: 1px solid #262c50; border-radius: 14px;
    padding: 16px 20px; min-width: 150px; }
  .stat .n { font-size: 30px; font-weight: 700; }
  .stat .l { color: #9aa0c9; font-size: 13px; margin-top: 2px; }
  .cols { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
  @media (max-width: 760px){ .cols { grid-template-columns: 1fr; } }
  .panel { background: #12152b; border: 1px solid #242a4c; border-radius: 16px; padding: 18px; }
  .panel h2 { font-size: 14px; text-transform: uppercase; letter-spacing: .1em;
    color: #aab0dd; margin-bottom: 14px; }
  .card { background: #1a1f3d; border: 1px solid #2c3360; border-radius: 12px;
    padding: 13px 15px; margin-bottom: 11px; animation: fade .3s ease; }
  @keyframes fade { from{opacity:0; transform: translateY(4px)} to{opacity:1} }
  .pair { display: flex; align-items: center; gap: 10px; }
  .pair .who { flex: 1; }
  .link { color: #6f76b0; font-size: 20px; }
  .phone { font-variant-numeric: tabular-nums; font-weight: 600; }
  .tags { margin-top: 7px; display: flex; gap: 6px; flex-wrap: wrap; }
  .t { font-size: 11px; padding: 3px 8px; border-radius: 999px;
    background: #242a4c; color: #c7ccf2; }
  .t.serious { background: #3a1f36; color: #ff9fce; }
  .t.friendship { background: #133532; color: #7ef0c2; }
  .t.casual { background: #3a2f16; color: #ffcf7a; }
  .empty { color: #6a6f96; font-size: 13px; padding: 10px 2px; }
</style>
</head>
<body>
  <div class="top">
    <span class="live"><span class="dot"></span>Live</span>
  </div>
  <h1>SemaMatch</h1>
  <div class="tag-line">Anonymous voice matchmaking — numbers are never exposed.</div>

  <div class="stats">
    <div class="stat"><div class="n" id="s-total">0</div><div class="l">Total callers</div></div>
    <div class="stat"><div class="n" id="s-queue">0</div><div class="l">Waiting in queue</div></div>
    <div class="stat"><div class="n" id="s-pairs">0</div><div class="l">Connected pairs</div></div>
  </div>

  <div class="cols">
    <div class="panel">
      <h2>Waiting in queue</h2>
      <div id="queue"></div>
    </div>
    <div class="panel">
      <h2>Connected</h2>
      <div id="pairs"></div>
    </div>
  </div>

<script>
  const mask = p => p ? '••• ••• ' + String(p).slice(-3) : '—';
  const tag = (v, cls) => v ? '<span class="t ' + (cls||'') + '">' + v + '</span>' : '';

  function cardHTML(c){
    return '<div class="card"><span class="phone">' + mask(c.phone_number) + '</span>' +
      '<div class="tags">' + tag(c.intent, c.intent) + tag(c.language) + tag(c.age_bracket) +
      '</div></div>';
  }

  function render(list){
    const queued = list.filter(c => c.status === 'queued');
    const matched = list.filter(c => c.status === 'matched');

    document.getElementById('s-total').textContent = list.length;
    document.getElementById('s-queue').textContent = queued.length;

    const byId = {};
    list.forEach(c => byId[c.session_id] = c);
    const seen = new Set();
    const pairs = [];
    matched.forEach(c => {
      if (seen.has(c.session_id)) return;
      const other = byId[c.match_session_id];
      if (other) { seen.add(c.session_id); seen.add(other.session_id); pairs.push([c, other]); }
    });

    document.getElementById('s-pairs').textContent = pairs.length;

    document.getElementById('queue').innerHTML = queued.length
      ? queued.map(cardHTML).join('')
      : '<div class="empty">No one waiting right now.</div>';

    document.getElementById('pairs').innerHTML = pairs.length
      ? pairs.map(([a,b]) =>
          '<div class="card pair"><div class="who">' + cardHTML(a) + '</div>' +
          '<div class="link">↔</div><div class="who">' + cardHTML(b) + '</div></div>').join('')
      : '<div class="empty">No live conversations yet.</div>';
  }

  async function tick(){
    try { const r = await fetch('/api/callers'); render(await r.json()); }
    catch (e) { /* backend momentarily unreachable */ }
  }
  tick(); setInterval(tick, 2000);
</script>
</body>
</html>
"""