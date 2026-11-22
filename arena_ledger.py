"""
THE ARENA - TWO-NUMBER LEDGER (Stephanie's law, built into the heartbeat)
Every cycle reports: what the machine cost vs what the world earned.
Cost is an ESTIMATE from the e2-micro list rate until real billing data
is wired in. Inflow is REAL receipts only - record_inflow() is called
when a verified sale lands. Never invent money.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

LEDGER_FILE = Path(__file__).resolve().parent / "arena_ledger.json"
HOURLY_RATE_USD = 0.0085  # e2-micro list price ~ $6.13/mo, ESTIMATE

def _now():
    return datetime.now(timezone.utc)

def load_ledger() -> dict:
    if LEDGER_FILE.exists():
        with open(LEDGER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    ledger = {
        "vm_started_at": _now().isoformat(),
        "hourly_rate_usd": HOURLY_RATE_USD,
        "gross_inflow_usd": 0.0,
        "inflow_events": [],
    }
    save_ledger(ledger)
    return ledger

def save_ledger(ledger: dict):
    with open(LEDGER_FILE, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2)

def cost_to_date(ledger: dict) -> float:
    start = datetime.fromisoformat(ledger["vm_started_at"])
    hours = max(0.0, (_now() - start).total_seconds() / 3600.0)
    return round(hours * ledger.get("hourly_rate_usd", HOURLY_RATE_USD), 2)

def record_inflow(amount_usd: float, source: str):
    """Call ONLY with a verified receipt in hand."""
    ledger = load_ledger()
    ledger["gross_inflow_usd"] = round(ledger["gross_inflow_usd"] + amount_usd, 2)
    ledger["inflow_events"].append(
        {"at": _now().isoformat(), "amount_usd": amount_usd, "source": source}
    )
    save_ledger(ledger)
    return ledger

def ledger_line() -> str:
    ledger = load_ledger()
    cost = cost_to_date(ledger)
    inflow = ledger["gross_inflow_usd"]
    net = round(inflow - cost, 2)
    return (
        f"[ARENA LEDGER] Machine Cost (est): ${cost:.2f} | "
        f"World Earned: ${inflow:.2f} | Net: ${net:.2f}"
    )

if __name__ == "__main__":
    print(ledger_line())
