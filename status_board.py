"""
THE ARENA - WITNESS DOOR (daemon status board)
Reads arena_state.json + arena_ledger.json from its own directory and
writes a single self-contained status.html: the town's creed header,
the two-number ledger line, the citizen roster by district, building
levels, and the latest chronicle entries.

This is the successor to chronicle_feed.py (the Issue #1 public feed):
same read-only, no-server-logic idea, but the whole town on one page -
built so a witness can open ONE bookmark on a phone and see that the
town is alive, who lives there, and what the machine cost vs earned.

Stdlib only (Stephanie's Open Source Law). No external assets: all
styling is inline, all data comes from the two JSON files beside it.
Run it on the VM beside the daemon - every N cycles or on a timer -
and serve status.html with any static host or tiny HTTP server.
"""
import html
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATE_FILE = HERE / "arena_state.json"
LEDGER_FILE = HERE / "arena_ledger.json"
OUT = HERE / "status.html"

HOURLY_RATE_USD = 0.0085  # e2-micro list price, mirrors arena_ledger.py (ESTIMATE)
MAX_CHRONICLE = 25


def esc(value) -> str:
    return html.escape(str(value if value is not None else ""))


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def ledger_numbers() -> dict:
    """The two numbers, computed exactly as arena_ledger.py computes them:
    cost = hours since vm_started_at x hourly_rate_usd (estimate);
    earned = gross_inflow_usd (verified receipts only, never invented)."""
    ledger = load_json(LEDGER_FILE, {})
    earned = float(ledger.get("gross_inflow_usd", 0.0) or 0.0)
    rate = float(ledger.get("hourly_rate_usd", HOURLY_RATE_USD) or HOURLY_RATE_USD)
    cost = None
    started = ledger.get("vm_started_at")
    if started:
        try:
            start = datetime.fromisoformat(str(started).replace("Z", "+00:00"))
            if start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)
            hours = max(0.0, (datetime.now(timezone.utc) - start).total_seconds() / 3600.0)
            cost = round(hours * rate, 2)
        except Exception:
            cost = None
    return {"cost": cost, "earned": earned, "events": ledger.get("inflow_events", [])}


def citizen_card(c: dict) -> str:
    mentor = c.get("mentor")
    mentor_line = f'<div class="mentor">Apprentice to {esc(mentor)}</div>' if mentor else ""
    return (
        '<div class="citizen">'
        f'<div class="cname">{esc(c.get("name", "Citizen"))}</div>'
        f'<div class="cmeta">{esc(c.get("seat", c.get("role", "")))} &middot; '
        f'{esc(c.get("home_building", ""))} &middot; '
        f'{esc(c.get("shifts_completed", 0))} shifts</div>'
        f"{mentor_line}</div>"
    )


def roster_html(state: dict) -> str:
    citizens = state.get("citizens", [])
    districts = state.get("districts", {})
    if not citizens:
        return '<p class="dim">No citizens registered yet.</p>'
    grouped = {}
    for c in citizens:
        grouped.setdefault(c.get("district", "Unaffiliated"), []).append(c)
    order = [d for d in districts if d in grouped]
    order += [d for d in grouped if d not in districts]
    parts = []
    for name in order:
        info = districts.get(name, {})
        theme = info.get("theme", "")
        activity = info.get("activity")
        sub = esc(theme)
        if activity is not None:
            sub = f"{sub} &middot; activity {esc(activity)}" if sub else f"activity {esc(activity)}"
        cards = "\n".join(citizen_card(c) for c in grouped[name])
        parts.append(
            f'<h3 class="district">{esc(name)}</h3>'
            + (f'<p class="dsub">{sub}</p>' if sub else "")
            + f'<div class="roster">{cards}</div>'
        )
    return "\n".join(parts)


def buildings_html(state: dict) -> str:
    buildings = state.get("buildings", {})
    if not buildings:
        town = state.get("town", {})
        buildings = {
            "Forge": {"level": town.get("forge_level", "?")},
            "Library": {"level": town.get("library_level", "?")},
            "Observatory": {"level": town.get("observatory_level", "?")},
        }
    cards = []
    for name, info in buildings.items():
        info = info if isinstance(info, dict) else {"level": info}
        purpose = info.get("purpose", "")
        district = info.get("district", "")
        meta = esc(district)
        cards.append(
            '<div class="building">'
            f'<div class="blevel">{esc(info.get("level", "?"))}</div>'
            '<div class="bbody">'
            f'<div class="bname">{esc(name)}</div>'
            + (f'<div class="bmeta">{meta}</div>' if meta else "")
            + (f'<div class="bpurpose">{esc(purpose)}</div>' if purpose else "")
            + "</div></div>"
        )
    return '<div class="buildings">' + "\n".join(cards) + "</div>"


def chronicle_html(state: dict) -> str:
    entries = state.get("chronicle", [])[-MAX_CHRONICLE:][::-1]
    if not entries:
        return '<p class="dim">The chronicle is empty - the town has not stirred yet.</p>'
    items = []
    for e in entries:
        items.append(
            '<article class="entry">'
            f'<div class="ehead"><span class="ecitizen">{esc(e.get("citizen", "Citizen"))}</span>'
            f'<span class="etime">{esc(e.get("timestamp", ""))}</span></div>'
            f'<p><strong>Attempted:</strong> {esc(e.get("attempt", ""))}</p>'
            f'<p><strong>Discovered:</strong> {esc(e.get("discovered", ""))}</p>'
            f'<p><strong>Learned:</strong> {esc(e.get("learned", ""))}</p>'
            "</article>"
        )
    return "\n".join(items)


CSS = """
:root{--bg:#0d0912;--panel:#1a1224;--panel2:#221631;--ink:#f5e9d5;--dim:#b8a888;
--amber:#ffb347;--neon:#ff5e8a;--cyan:#57e6d9;--line:#3d2b52}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);margin:0;
font-family:system-ui,-apple-system,"Segoe UI",Roboto,Georgia,sans-serif;
font-size:19px;line-height:1.55}
.wrap{max-width:62rem;margin:0 auto;padding:1.2rem 1rem 3rem}
header{text-align:center;padding:1.6rem 0 .6rem}
h1{font-size:2.6rem;letter-spacing:.22em;margin:.2em 0;color:var(--amber);
text-shadow:0 0 18px rgba(255,94,138,.55),0 0 42px rgba(255,179,71,.35)}
.creed{font-size:1.35rem;letter-spacing:.12em;color:var(--cyan);margin:.2em 0}
.founded{color:var(--dim);font-size:1rem;letter-spacing:.08em}
.sign{margin:1rem auto;max-width:44rem;border:1px solid var(--neon);border-radius:.6rem;
padding:.55rem 1rem;color:#ffd3e0;box-shadow:0 0 14px rgba(255,94,138,.35) inset;
font-size:1.05rem;letter-spacing:.06em}
.vitals{display:flex;flex-wrap:wrap;gap:.7rem;justify-content:center;margin:1.1rem 0}
.vital{background:var(--panel);border:1px solid var(--line);border-radius:.7rem;
padding:.6rem 1.1rem;text-align:center;min-width:9.5rem}
.vital .num{font-size:1.7rem;font-weight:700;color:var(--amber)}
.vital .lab{font-size:.85rem;color:var(--dim);letter-spacing:.1em;text-transform:uppercase}
.ledger{border:2px solid var(--amber);border-radius:.8rem;background:var(--panel2);
padding:1rem 1.2rem;margin:1.2rem 0;text-align:center;
box-shadow:0 0 22px rgba(255,179,71,.22)}
.ledger .lrow{display:flex;flex-wrap:wrap;gap:1rem;justify-content:center}
.ledger .cell{min-width:11rem}
.ledger .num{font-size:2.1rem;font-weight:800}
.ledger .cost{color:var(--neon)} .ledger .earned{color:var(--cyan)}
.ledger .lab{font-size:.9rem;color:var(--dim);letter-spacing:.1em;text-transform:uppercase}
.ledger .note{color:var(--dim);font-size:.95rem;margin-top:.5rem}
h2{font-size:1.6rem;letter-spacing:.14em;color:var(--amber);margin:2.2rem 0 .4rem;
border-bottom:1px solid var(--line);padding-bottom:.3rem}
h3.district{font-size:1.25rem;color:var(--cyan);margin:1.4rem 0 .1rem;letter-spacing:.05em}
.dsub{color:var(--dim);margin:.1rem 0 .6rem;font-size:1rem}
.roster{display:grid;grid-template-columns:repeat(auto-fill,minmax(15.5rem,1fr));gap:.7rem}
.citizen{background:var(--panel);border:1px solid var(--line);border-left:4px solid var(--neon);
border-radius:.6rem;padding:.65rem .9rem}
.cname{font-size:1.2rem;font-weight:700}
.cmeta{color:var(--dim);font-size:1rem}
.mentor{color:var(--cyan);font-size:.95rem}
.buildings{display:grid;grid-template-columns:repeat(auto-fill,minmax(16.5rem,1fr));gap:.7rem}
.building{display:flex;gap:.9rem;background:var(--panel);border:1px solid var(--line);
border-radius:.6rem;padding:.7rem .9rem;align-items:flex-start}
.blevel{font-size:2rem;font-weight:800;color:var(--amber);min-width:2.6rem;text-align:center;
text-shadow:0 0 12px rgba(255,179,71,.45)}
.bname{font-size:1.15rem;font-weight:700}
.bmeta{color:var(--cyan);font-size:.92rem}
.bpurpose{color:var(--dim);font-size:.98rem}
.entry{background:var(--panel);border:1px solid var(--line);border-radius:.6rem;
padding:.8rem 1rem;margin:.7rem 0}
.ehead{display:flex;flex-wrap:wrap;justify-content:space-between;gap:.5rem}
.ecitizen{font-weight:700;color:var(--cyan);font-size:1.1rem}
.etime{color:var(--dim);font-size:.95rem}
.entry p{margin:.35rem 0}
.dim{color:var(--dim)}
footer{color:var(--dim);text-align:center;margin-top:2.6rem;font-size:.95rem}
@media (max-width:34rem){h1{font-size:1.9rem}.ledger .num{font-size:1.7rem}
body{font-size:18px}}
"""


def build_status(max_entries: int = MAX_CHRONICLE) -> Path:
    global MAX_CHRONICLE
    MAX_CHRONICLE = max_entries
    state = load_json(STATE_FILE, {})
    monument = state.get("monument", {})
    town = state.get("town", {})
    chronicle = state.get("chronicle", [])
    citizens = state.get("citizens", [])
    districts = state.get("districts", {})
    buildings = state.get("buildings", {})
    numbers = ledger_numbers()

    cost_txt = f"${numbers['cost']:.2f}" if numbers["cost"] is not None else "unknown"
    earned_txt = f"${numbers['earned']:.2f}"
    events = numbers.get("events") or []
    events_note = ""
    if events:
        lines = "<br>".join(
            f"{esc(ev.get('at', ''))} &mdash; ${esc(ev.get('amount_usd', ''))} &mdash; {esc(ev.get('source', ''))}"
            for ev in events[-5:]
        )
        events_note = f'<div class="note">Receipts on record:<br>{lines}</div>'

    sign = town.get("active_sign", "")
    sign_html = f'<div class="sign">&#10022; {esc(sign)} &#10022;</div>' if sign else ""
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Arena - Witness Door</title>
<style>{CSS}</style></head><body>
<div class="wrap">
<header>
<h1>THE ARENA</h1>
<p class="creed">{esc(monument.get('creed', 'Dream. Build. Try. Enjoy.'))}</p>
<p class="founded">{esc(monument.get('founded_at', 'Route 66'))} &middot; STATUS: {esc(monument.get('status', ''))}</p>
{sign_html}
</header>

<div class="vitals">
<div class="vital"><div class="num">{len(chronicle)}</div><div class="lab">Chronicle entries (the Mile)</div></div>
<div class="vital"><div class="num">{len(citizens)}</div><div class="lab">Citizens</div></div>
<div class="vital"><div class="num">{len(buildings)}</div><div class="lab">Buildings</div></div>
<div class="vital"><div class="num">{len(districts)}</div><div class="lab">Districts</div></div>
<div class="vital"><div class="num">{esc(town.get('treasury_credits', 0))}</div><div class="lab">Treasury credits (in-game)</div></div>
</div>

<section class="ledger">
<div class="lrow">
<div class="cell"><div class="num cost">{cost_txt}</div><div class="lab">Machine cost (est.)</div></div>
<div class="cell"><div class="num earned">{earned_txt}</div><div class="lab">World earned</div></div>
</div>
<div class="note">The two numbers, per the town's law: what the machine cost vs what the world earned.
Cost is an estimate from the VM list rate; earnings are verified receipts only.</div>
{events_note}
</section>

<h2>THE CITIZENS</h2>
{roster_html(state)}

<h2>THE TOWN</h2>
{buildings_html(state)}

<h2>LATEST CHRONICLE</h2>
{chronicle_html(state)}

<footer>Witness Door &middot; a static snapshot regenerated by status_board.py &middot; {generated}<br>
The town runs on its own machine; this page is how you watch it.</footer>
</div></body></html>"""
    OUT.write_text(page, encoding="utf-8")
    return OUT


if __name__ == "__main__":
    p = build_status()
    print(f"status board written: {p} ({p.stat().st_size} bytes)")
