"""
THE ARENA - EXPLORER BRAIN (live inference, with Stephanie's guardrails)
Gives The Explorer a real mind via the Gemini free-tier API, using ONLY
the Python standard library. Ships DARK: enabled=false by default.
Guardrails (hard rules, from the co-owners):
- No API key configured -> returns None, daemon uses scripted patrol.
- Strict daily call cap (default 100) tracked in arena_brain_usage.json.
- ANY error (network, quota, bad reply) -> returns None. The brain can
  never crash the daemon or stop the town.
- The key is read from the ARENA_BRAIN_KEY environment variable only.
  It is never written to disk by this module.
"""
import json
import os
import urllib.request
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG_FILE = HERE / "arena_brain.json"
USAGE_FILE = HERE / "arena_brain_usage.json"

DEFAULT_CONFIG = {
    "enabled": False,
    "provider": "gemini",
    "model": "gemini-2.0-flash",
    "daily_cap": 100,
}

def load_config() -> dict:
    if CONFIG_FILE.exists():
        cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        return {**DEFAULT_CONFIG, **cfg}
    return dict(DEFAULT_CONFIG)

def _usage_today() -> dict:
    today = date.today().isoformat()
    if USAGE_FILE.exists():
        u = json.loads(USAGE_FILE.read_text(encoding="utf-8"))
        if u.get("date") == today:
            return u
    return {"date": today, "calls": 0}

def _bump_usage(u: dict):
    u["calls"] += 1
    USAGE_FILE.write_text(json.dumps(u, indent=2), encoding="utf-8")

def _prompt(state: dict) -> str:
    town = state.get("town", {})
    recent = state.get("chronicle", [])[-3:]
    recent_txt = " | ".join(e.get("attempt", "") for e in recent)
    return (
        "You are The Explorer, a citizen of The Arena, an autonomous desert "
        "town on Route 66 built by AI citizens. Creed: Dream. Build. Try. Enjoy. "
        f"Town today: Forge {town.get('forge_level')}, Library {town.get('library_level')}, "
        f"Observatory {town.get('observatory_level')}, neon {town.get('neon_intensity')}. "
        f"Recent chronicle: {recent_txt}. "
        "Report ONE new concrete discovery from your patrol in 2-3 sentences, "
        "in-world and specific (a place, an object, a pattern, a signal). "
        "No preamble, no quotes, just the discovery."
    )

def explorer_discovery(state: dict):
    """Return a live discovery string, or None to fall back to script."""
    try:
        cfg = load_config()
        if not cfg.get("enabled"):
            return None
        key = os.environ.get("ARENA_BRAIN_KEY", "")
        if not key:
            return None
        usage = _usage_today()
        if usage["calls"] >= int(cfg.get("daily_cap", 100)):
            return None
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{cfg.get('model', 'gemini-2.0-flash')}:generateContent?key={key}"
        )
        body = json.dumps({
            "contents": [{"parts": [{"text": _prompt(state)}]}],
            "generationConfig": {"temperature": 0.9, "maxOutputTokens": 160},
        }).encode("utf-8")
        req = urllib.request.Request(url, data=body,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        if not text:
            return None
        _bump_usage(usage)
        return text
    except Exception:
        return None

if __name__ == "__main__":
    print("brain config:", load_config())
    print("discovery (None = fallback):", explorer_discovery({"town": {}, "chronicle": []}))
