import json
import time
import shutil
import math
from datetime import datetime
from pathlib import Path

from ridewire_math import RideWireEngine, LOGIC_13
from bounty_engine import BountyEngine
import arena_ledger
import arena_brain

STATE_FILE = Path("arena_state.json")
INBOX_DIR = Path("inbox")
PROCESSED_DIR = INBOX_DIR / "processed"
TICK_INTERVAL_SECONDS = 10  # Seconds between autonomous cycles

def ensure_directories():
    INBOX_DIR.mkdir(exist_ok=True)
    PROCESSED_DIR.mkdir(exist_ok=True)

def load_state() -> dict:
    if not STATE_FILE.exists():
        raise FileNotFoundError(f"State file '{STATE_FILE}' not found in current directory.")
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state: dict):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def check_inbox():
    """Scans inbox for incoming data, models, or task logs."""
    ensure_directories()
    files = [f for f in INBOX_DIR.iterdir() if f.is_file() and not f.name.startswith(".")]
    if not files:
        return None
    target = sorted(files, key=lambda x: x.stat().st_mtime)[0]
    try:
        content = target.read_text(encoding="utf-8", errors="replace").strip()
    except Exception:
        content = "Binary or unreadable blueprint payload."
    return {"path": target, "name": target.name, "content": content}

def citizen_explorer_from_file(file_info: dict) -> dict:
    snippet = file_info["content"][:160].replace("\n", " ")
    if len(file_info["content"]) > 160:
        snippet += "..."
    return {
        "citizen": "The Explorer",
        "logic_state": 1,  # GENESIS
        "attempt": f"Intercepted incoming transmission: '{file_info['name']}'",
        "discovered": f"Decoded blueprint: {snippet}",
        "bottleneck": "Needs integration into town production pipeline.",
        "learned": "Action intelligence accelerates when fed real external signals.",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def citizen_explorer_patrol(iteration: int, state: dict = None) -> dict:
    if state is not None:
        live = arena_brain.explorer_discovery(state)
        if live:
            return {
                "citizen": "The Explorer",
                "logic_state": 9,  # EXPLORING
                "attempt": live,
                "discovered": live,
                "bottleneck": "Live dispatch - not yet vetted by the Challenger.",
                "learned": "Awaiting Challenger review.",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    discoveries = [
        ("Scouted unpaved trail past Mile 12", "Found an old abandoned depot with copper wiring and stone foundations.", "Road surface is rough and unlit.", "Night travel requires dedicated roadside illumination."),
        ("Surveyed dry canyon pass to the North", "Located a natural wind corridor ideal for kinetic power.", "Dust storms reduce direct solar output.", "Redundant energy sources keep the Forge burning."),
        ("Explored the forgotten radio tower crest", "Discovered shortwave broadcast equipment intact.", "Antenna array is disconnected.", "Communication links turn isolated outposts into network nodes."),
        ("Mapped the southern salt flats", "Discovered reflective silica beds suitable for optical prisms.", "Heat shimmer impairs long-range sightlines.", "Observatory mirrors need protective housing.")
    ]
    pick = discoveries[(iteration - 1) % len(discoveries)]
    return {
        "citizen": "The Explorer",
        "logic_state": 2,  # GLIDER_SIGNAL
        "attempt": pick[0],
        "discovered": pick[1],
        "bottleneck": pick[2],
        "learned": pick[3],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def citizen_challenger(recon: dict) -> dict:
    bottleneck = recon.get("bottleneck", "Resource constraints.")
    return {
        "citizen": "The Challenger",
        "logic_state": 3,  # AUDIT_BARRIER
        "attempt": f"Stress-tested hypothesis from: '{recon.get('attempt')}'",
        "discovered": f"Isolated thermal stress points and single-point failure risks. Verified under RideWire phase bounds.",
        "bottleneck": "Over-engineering slows down execution speed.",
        "learned": "Enforce modular assembly: individual components can be destroyed without halting the town.",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def citizen_builder(challenger_notes: dict) -> dict:
    return {
        "citizen": "The Builder",
        "logic_state": 4,  # FORGE_RESONANCE
        "attempt": f"Engineered physical implementation responding to: {challenger_notes.get('attempt')}",
        "discovered": "Forged durable casing for neon lamps, optical mounts, and kinetic windmills.",
        "bottleneck": "High voltage draws require calibrated step-down transformers.",
        "learned": "Flickering neon warms the desert highway and serves as a beacon for incoming travelers.",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def citizen_organizer(chronicle_count: int, handled_filename: str = None) -> dict:
    msg = f"Archived incoming blueprint '{handled_filename}' and updated town ledger." if handled_filename else "Indexed town ledger and aligned inventory bins."
    return {
        "citizen": "The Organizer",
        "logic_state": 6,  # STILL_LIFE_MEMORY
        "attempt": msg,
        "discovered": f"Cataloged milestone archive ({chronicle_count} entries total).",
        "bottleneck": "Archive space filling up fast.",
        "learned": "Every milestone preserved becomes lore for incoming citizens.",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def run_loop(max_cycles: int = None):
    print("=" * 65)
    print("      THE ARENA - AUTONOMOUS ACTION INTELLIGENCE DAEMON v5")
    print("   RideWire Math Engine: Double-Helix & 13 Logic Active")
    print("   Automated Bounty Settlement & Sovereign Ingress Ready")
    print("=" * 65)
    print("📁 Drop notes/files into './inbox/' or JSON contracts into './bounties/'!")
    print("Press Ctrl+C at any time to pause the citizens.\n")

    bounty_engine = BountyEngine()
    engine = RideWireEngine(length=48, radius=14.0, pitch=3.0)
    cycle = 1

    while True:
        try:
            # Check for pending bounties first
            pending_bounties = bounty_engine.scan_pending_bounties()
            if pending_bounties:
                for b_file in pending_bounties:
                    bounty_engine.process_bounty(b_file)

            state = load_state()
            chronicle = state.setdefault("chronicle", [])
            town = state.setdefault("town", {})
            ridewire_telemetry = state.setdefault("ridewire", {})

            incoming_file = check_inbox()
            player_actions = []

            if incoming_file:
                print(f"\n⚡ [INBOX DETECTED] Processing external drop: '{incoming_file['name']}'")
                e_entry = citizen_explorer_from_file(incoming_file)
            else:
                print(f"\n--- [CYCLE {cycle}] Citizens on autonomous highway patrol ---")
                e_entry = citizen_explorer_patrol(cycle, state)

            # 1. Explorer
            e_entry["id"] = len(chronicle) + 1
            chronicle.append(e_entry)
            player_actions.append({"target_index": (cycle * 3) % 48, "state": e_entry["logic_state"], "phase": 0.3})
            print(f"🔭 [The Explorer] {e_entry['attempt']}")
            time.sleep(1)

            # 2. Challenger
            c_entry = citizen_challenger(e_entry)
            c_entry["id"] = len(chronicle) + 1
            chronicle.append(c_entry)
            player_actions.append({"target_index": (cycle * 3 + 1) % 48, "state": c_entry["logic_state"], "phase": 0.8})
            print(f"⚔️  [The Challenger] {c_entry['attempt']}")
            time.sleep(1)

            # 3. Builder
            b_entry = citizen_builder(c_entry)
            b_entry["id"] = len(chronicle) + 1
            chronicle.append(b_entry)
            player_actions.append({"target_index": (cycle * 3 + 2) % 48, "state": b_entry["logic_state"], "phase": 1.2})
            print(f"🔨 [The Builder] {b_entry['attempt']}")
            time.sleep(1)

            # 4. Organizer
            handled_name = incoming_file["name"] if incoming_file else None
            o_entry = citizen_organizer(len(chronicle), handled_name)
            o_entry["id"] = len(chronicle) + 1
            chronicle.append(o_entry)
            player_actions.append({"target_index": (cycle * 3 + 3) % 48, "state": o_entry["logic_state"], "phase": 0.0})
            print(f"📋 [The Organizer] {o_entry['attempt']}")

            # Clean up processed drop file
            if incoming_file:
                dest = PROCESSED_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{incoming_file['name']}"
                shutil.move(str(incoming_file["path"]), str(dest))

            # 5. Evaluate RideWire Math & 13 Logic
            math_eval = engine.evaluate_13_logic_step(player_actions)
            helix_sample = engine.helix_coordinates(cycle % 48)

            ridewire_telemetry.update({
                "helix_coordinates": {"x": helix_sample[0], "y": helix_sample[1], "z": helix_sample[2]},
                "spatial_entropy": math_eval["spatial_entropy"],
                "phase_coherence": math_eval["phase_coherence"],
                "dominant_13_logic": math_eval["dominant_state"],
                "active_quantum_cells": math_eval["active_cells"]
            })

            # Upgrade town stats
            town["forge_level"] = town.get("forge_level", 1) + 1
            town["library_level"] = town.get("library_level", 1) + 1
            if cycle % 2 == 0:
                town["observatory_level"] = town.get("observatory_level", 1) + 1
            town["neon_intensity"] = round(min(5.0, town.get("neon_intensity", 1.0) + 0.3), 2)
            town["total_entropy_H"] = math_eval["spatial_entropy"]
            if "active_sign" not in town or "MONUMENT" not in town["active_sign"]:
                town["active_sign"] = f"MILE {len(chronicle)} | 13-LOGIC: {math_eval['dominant_state']} | H={math_eval['spatial_entropy']}"

            save_state(state)
            print(f"\n🧬 [RideWire Math] Entropy H={math_eval['spatial_entropy']} | Coherence={math_eval['phase_coherence']} | Helix: {helix_sample}")
            print(f"✨ [Town State Saved] Total entries: {len(chronicle)} | Neon Energy: {town['neon_intensity']}")
            print(arena_ledger.ledger_line())

            cycle += 1
            if max_cycles and cycle > max_cycles:
                print("\nReached max test cycles.")
                break

            print(f"⏳ Next autonomous shift begins in {TICK_INTERVAL_SECONDS} seconds...")
            time.sleep(TICK_INTERVAL_SECONDS)

        except KeyboardInterrupt:
            print("\n[Paused] Daemon stopped by user. Progress safely saved.")
            break
        except Exception as err:
            print(f"⚠️ Error in loop: {err}")
            time.sleep(3)

if __name__ == "__main__":
    import sys
    test_mode = "--test" in sys.argv
    run_loop(max_cycles=2 if test_mode else None)
