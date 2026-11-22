"""
THE ARENA - PUBLIC CHRONICLE FEED
Reads arena_state.json and writes a single self-contained feed.html:
the town's latest chronicle entries, building levels, and the
two-number ledger line. No dependencies, no server logic - the file
can be served by any static host or a tiny HTTP server on the VM.
"""
import json
import html
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATE = HERE / "arena_state.json"
OUT = HERE / "feed.html"

def build_feed(max_entries: int = 25) -> Path:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    town = state.get("town", {})
    chronicle = state.get("chronicle", [])[-max_entries:][::-1]
    try:
        import arena_ledger
        ledger = arena_ledger.ledger_line()
    except Exception:
        ledger = "[ARENA LEDGER] unavailable"
    rows = "\n".join(
        f"<li><strong>{html.escape(str(e.get('citizen', 'Citizen')))}</strong> — "
        f"{html.escape(str(e.get('attempt', '')))}</li>"
        for e in chronicle
    )
    page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>The Arena — Live Chronicle</title>
<style>body{{background:#14100c;color:#f3e2c7;font-family:Georgia,serif;max-width:44em;margin:2em auto;padding:0 1em}}
h1{{letter-spacing:.15em}} .ledger{{border:1px solid #a67c3d;padding:.6em 1em;margin:1em 0;color:#ffd98a}}
li{{margin:.45em 0;line-height:1.45}}</style></head><body>
<h1>WELCOME TO THE ARENA</h1>
<p><em>The road ahead is unfinished. This town builds itself — watch.</em></p>
<div class="ledger">{html.escape(ledger)}</div>
<p>Forge {town.get('forge_level')} · Library {town.get('library_level')} ·
Observatory {town.get('observatory_level')} · Neon {town.get('neon_intensity')} ·
Treasury {town.get('treasury_credits')} credits (in-game)</p>
<h2>Latest Chronicle</h2><ul>
{rows}
</ul></body></html>"""
    OUT.write_text(page, encoding="utf-8")
    return OUT

if __name__ == "__main__":
    p = build_feed()
    print(f"feed written: {p} ({p.stat().st_size} bytes)")
