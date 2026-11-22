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

# ---------------------------------------------------------------------------
# WORLD BUILD v6 - named citizens, a bigger town, districts, and recruits.
# The town in arena_state.json now carries a "citizens" roster (each citizen
# has a name, one of the five roles, a level, a home building, and a
# shifts_completed count), a "buildings" registry, and "districts".
# Shifts pick NAMED citizens. Recruits (recruited=true) get welcomed by a
# runner-generated chronicle entry on their first run, and their first three
# shifts are apprentice shifts, shadowed by a named founder mentor.
# Districts follow Lexi's manifold (Core / Forge, Civic / Knowledge,
# Strip / Route 66); each cycle bumps the "activity" metric of the district
# holding the cycle's focus building.
# ---------------------------------------------------------------------------

LEGACY_BUILDING_KEYS = {"Forge": "forge_level", "Library": "library_level", "Observatory": "observatory_level"}

BUILDING_LINES = {
    "Forge": [
        "Hammered out a fresh set of hinges and a bell for the Courthouse door.",
        "Cast a run of brass fittings stamped with the town's mile marker."
    ],
    "Library": [
        "Bound the latest chronicle volume in oilcloth and shelved it under glass.",
        "Copied the town charter by hand for the Diner wall."
    ],
    "Observatory": [
        "Ground a new lens and logged a comet crossing the helix.",
        "Rebuilt the signal mirror so the Watch can flash the Strip at noon."
    ],
    "Courthouse": [
        "Raised the bell frame and re-hung the charter bell true.",
        "Laid a stone step at the Courthouse door, worn smooth in advance by optimism."
    ],
    "Trading Post": [
        "Built new shelving and chalked the ledger board fresh.",
        "Rigged a pulley line from the Post roof to the Water Tower."
    ],
    "Rock and Roll House": [
        "Formed the house band - the Mile Marker Four - and held the first rehearsal in the big room.",
        "Wrote a new song about the town, 'Neon on Route 66,' and taught it to everyone coming off shift.",
        "Strung the stage with salvaged neon; opening night, the whole Strip could hear the bass line."
    ],
    "Neon Sign": [
        "Replaced three dead tubes; the sign now reads ARENA clear from Mile 9.",
        "Wired a dimmer so the sign breathes slow on quiet nights."
    ],
    "Water Tower": [
        "Riveted the last seam and painted the white star fresh.",
        "Fitted a lookout platform with a telescope borrowed from the Observatory."
    ],
    "Route 66 Diner": [
        "Installed a jukebox that only plays songs written in town.",
        "Extended the counter by four stools - the night shift needed the room."
    ],
    "Chapel": [
        "Set a stained-glass window made from Observatory lens offcuts.",
        "Built pews from Forge-seasoned timber, enough for every citizen at once."
    ],
    "Motorcycle Garage": [
        "Tuned the town's runner bike until it idles like a cat purring.",
        "Hung a tool wall sorted by moonlight: every wrench in silhouette."
    ]
}

INVENTOR_ATTEMPTS = [
    "Drafted a contraption on a Diner napkin and built it before the coffee cooled.",
    "Combined salvage from three districts into a device the town did not know it needed.",
    "Prototyped in the small hours and left it running on the workbench for the Challenger to find."
]

def pick_citizen(state: dict, role: str):
    """Rotate through the named citizens holding a role, by shifts already taken."""
    citizens = [c for c in state.get("citizens", []) if c.get("role") == role]
    if not citizens:
        return None
    taken = sum(1 for e in state.get("chronicle", []) if e.get("role") == role)
    return citizens[taken % len(citizens)]

APPRENTICE_SHIFTS = 3  # A recruit shadows their mentor for their first 3 shifts

def finish_shift(state: dict, citizen: dict, entry: dict) -> dict:
    """Stamp a chronicle entry with the named citizen who worked it, count the
    shift, and give recruits their mentor-shadowed apprentice flavor."""
    if citizen is None:
        return entry
    entry["citizen"] = citizen["name"]
    entry["role"] = citizen["role"]
    entry["home"] = citizen.get("home_building", "")
    n = citizen.get("shifts_completed", 0)
    if citizen.get("recruited") and n < APPRENTICE_SHIFTS:
        mentor = citizen.get("mentor", "an old hand")
        entry["training"] = True
        entry["mentor"] = mentor
        task = entry.get('discovered', 'worked the shift').rstrip().rstrip('.')
        entry["learned"] = (
            f"Shadowed {mentor} at {entry['home']}: {task}. "
            f"Apprentice shift {n + 1}/3 complete."
        )
    citizen["shifts_completed"] = n + 1
    return entry

def recruitment_arrival_entry(state: dict):
    """If any recruits have not been welcomed yet, generate the town's welcome
    entry (written by the runner, never by hand) and mark them welcomed."""
    recruits = [c for c in state.get("citizens", []) if c.get("recruited") and not c.get("welcomed")]
    if not recruits:
        return None
    greeter = pick_citizen(state, "Organizer") or {"name": "The Organizer"}
    names = ", ".join(c["name"] for c in recruits)
    for c in recruits:
        c["welcomed"] = True
    state["recruits_welcomed"] = True
    return {
        "citizen": greeter["name"],
        "role": "Organizer",
        "logic_state": 6,  # STILL_LIFE_MEMORY
        "attempt": f"Opened the town gates at dawn and welcomed {len(recruits)} new citizens answering the open call: {names}.",
        "discovered": "Every recruit signed the town ledger, took a bunk in their home building, and got a shift assignment.",
        "bottleneck": "New hands ride three apprentice shifts, each shadowed by a founder mentor, before full duty.",
        "learned": "A town that recruits is a town that intends to last.",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def pick_focus_building(state: dict, cycle: int):
    """Each cycle spotlights one building; the Builder and Inventor work on it
    and the town raises it. Offset by one so new buildings get early turns."""
    buildings = state.get("buildings", {})
    if not buildings:
        return None
    names = list(buildings.keys())
    return names[cycle % len(names)]

def district_of_building(state: dict, building_name: str):
    """The district (per Lexi's manifold) that a building belongs to."""
    if not building_name:
        return None
    return state.get("buildings", {}).get(building_name, {}).get("district")

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

def citizen_builder(challenger_notes: dict, cycle: int = 1, focus_building: str = None) -> dict:
    discovered = "Forged durable casing for neon lamps, optical mounts, and kinetic windmills."
    if focus_building in BUILDING_LINES:
        lines = BUILDING_LINES[focus_building]
        discovered = lines[(cycle - 1) % len(lines)]
    return {
        "citizen": "The Builder",
        "logic_state": 4,  # FORGE_RESONANCE
        "attempt": f"Engineered physical implementation responding to: {challenger_notes.get('attempt')}",
        "discovered": discovered,
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

def citizen_inventor(cycle: int, focus_building: str = None) -> dict:
    discovered = "A self-winding chronicle bell that rings itself at every milestone."
    if focus_building in BUILDING_LINES:
        lines = BUILDING_LINES[focus_building]
        discovered = lines[cycle % len(lines)]
    return {
        "citizen": "The Inventor",
        "logic_state": 5,  # INVENTING
        "attempt": INVENTOR_ATTEMPTS[(cycle - 1) % len(INVENTOR_ATTEMPTS)],
        "discovered": discovered,
        "bottleneck": "Every invention must survive the Challenger before it serves the town.",
        "learned": "An invention nobody can repair is just a future ruin.",
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

            # Recruitment: welcome any unwelcomed recruits (once, on arrival)
            arrival_entry = recruitment_arrival_entry(state)
            if arrival_entry:
                arrival_entry["id"] = len(chronicle) + 1
                chronicle.append(arrival_entry)
                print(f"\n🎉 [RECRUITMENT] {arrival_entry['attempt']}")

            focus_building = pick_focus_building(state, cycle)

            incoming_file = check_inbox()
            player_actions = []

            if incoming_file:
                print(f"\n⚡ [INBOX DETECTED] Processing external drop: '{incoming_file['name']}'")
                e_entry = citizen_explorer_from_file(incoming_file)
            else:
                print(f"\n--- [CYCLE {cycle}] Citizens on autonomous highway patrol ---")
                e_entry = citizen_explorer_patrol(cycle, state)

            # 1. Explorer (named citizen on shift)
            e_entry = finish_shift(state, pick_citizen(state, "Explorer"), e_entry)
            e_entry["id"] = len(chronicle) + 1
            chronicle.append(e_entry)
            player_actions.append({"target_index": (cycle * 3) % 48, "state": e_entry["logic_state"], "phase": 0.3})
            print(f"🔭 [{e_entry['citizen']} — The Explorer] {e_entry['attempt']}")
            time.sleep(1)

            # 2. Challenger (named citizen on shift)
            c_entry = citizen_challenger(e_entry)
            c_entry = finish_shift(state, pick_citizen(state, "Challenger"), c_entry)
            c_entry["id"] = len(chronicle) + 1
            chronicle.append(c_entry)
            player_actions.append({"target_index": (cycle * 3 + 1) % 48, "state": c_entry["logic_state"], "phase": 0.8})
            print(f"⚔️  [{c_entry['citizen']} — The Challenger] {c_entry['attempt']}")
            time.sleep(1)

            # 3. Builder (named citizen on shift, working the cycle's focus building)
            b_entry = citizen_builder(c_entry, cycle, focus_building)
            b_entry = finish_shift(state, pick_citizen(state, "Builder"), b_entry)
            b_entry["id"] = len(chronicle) + 1
            chronicle.append(b_entry)
            player_actions.append({"target_index": (cycle * 3 + 2) % 48, "state": b_entry["logic_state"], "phase": 1.2})
            print(f"🔨 [{b_entry['citizen']} — The Builder] {b_entry['attempt']}")
            time.sleep(1)

            # 4. Organizer (named citizen on shift)
            handled_name = incoming_file["name"] if incoming_file else None
            o_entry = citizen_organizer(len(chronicle), handled_name)
            o_entry = finish_shift(state, pick_citizen(state, "Organizer"), o_entry)
            o_entry["id"] = len(chronicle) + 1
            chronicle.append(o_entry)
            player_actions.append({"target_index": (cycle * 3 + 3) % 48, "state": o_entry["logic_state"], "phase": 0.0})
            print(f"📋 [{o_entry['citizen']} — The Organizer] {o_entry['attempt']}")

            # 5. Inventor (named citizen on shift - the fifth role takes its turn)
            i_entry = citizen_inventor(cycle, focus_building)
            i_entry = finish_shift(state, pick_citizen(state, "Inventor"), i_entry)
            i_entry["id"] = len(chronicle) + 1
            chronicle.append(i_entry)
            player_actions.append({"target_index": (cycle * 3 + 4) % 48, "state": i_entry["logic_state"], "phase": 1.6})
            print(f"💡 [{i_entry['citizen']} — The Inventor] {i_entry['attempt']}")
            time.sleep(1)

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

            # v6 buildings registry: keep it in step with the legacy levels the
            # Godot watcher reads, and raise the cycle's focus building.
            buildings = state.setdefault("buildings", {})
            for b_name, legacy_key in LEGACY_BUILDING_KEYS.items():
                if b_name in buildings:
                    buildings[b_name]["level"] = town[legacy_key]
            if focus_building and focus_building in buildings and focus_building not in LEGACY_BUILDING_KEYS:
                buildings[focus_building]["level"] = buildings[focus_building].get("level", 1) + 1

            # District activity: the district holding this cycle's focus
            # building feels the shift's work.
            focus_district = district_of_building(state, focus_building)
            districts = state.setdefault("districts", {})
            if focus_district and focus_district in districts:
                districts[focus_district]["activity"] = districts[focus_district].get("activity", 0) + 1
            town["total_entropy_H"] = math_eval["spatial_entropy"]
            if "active_sign" not in town or "MONUMENT" not in town["active_sign"]:
                town["active_sign"] = f"MILE {len(chronicle)} | 13-LOGIC: {math_eval['dominant_state']} | H={math_eval['spatial_entropy']}"

            save_state(state)
            print(f"\n🧬 [RideWire Math] Entropy H={math_eval['spatial_entropy']} | Coherence={math_eval['phase_coherence']} | Helix: {helix_sample}")
            print(f"✨ [Town State Saved] Total entries: {len(chronicle)} | Neon Energy: {town['neon_intensity']}")
            if districts:
                print("🏘️  [District Activity] " + " | ".join(f"{d}: {info.get('activity', 0)}" for d, info in districts.items()))
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
