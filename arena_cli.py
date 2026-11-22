#!/usr/bin/env python3
"""
THE ARENA - ACTING OWNER EXECUTIVE MANAGEMENT CONSOLE
Provides sovereign executive commands over The Arena ecosystem:
bounties, agent gladiators, RideWire phase dynamics, and treasury reserves.
"""

import sys
import json
import argparse
from pathlib import Path
from ridewire_math import LOGIC_13
from arena_agent_protocol import ArenaAgentProtocol
from bounty_engine import BountyEngine
from town_treasury import TownTreasury

STATE_FILE = Path("arena_state.json")

def cmd_status(args):
    if not STATE_FILE.exists():
        print("World state not found. Launch the daemon first.")
        return
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        world = json.load(f)
    town = world.get("town", {})
    chronicle = world.get("chronicle", [])
    treasury = TownTreasury().get_summary()

    print("\n" + "=" * 62)
    print("       🏜️  THE ARENA - EXECUTIVE SOVEREIGN STATUS")
    print("=" * 62)
    print(f"📍 Highway Coordinates : Route 66 | Mile {len(chronicle)}")
    print(f"🏛️  Town Structures     : Forge Lv.{town.get('forge_level', 1)} | Library Lv.{town.get('library_level', 1)} | Observatory Lv.{town.get('observatory_level', 1)}")
    print(f"💡 Neon Marquee        : {town.get('neon_intensity', 1.0)}x Glow | '{town.get('active_sign', 'WELCOME')}'")
    print(f"🧬 Spatial Entropy (H) : {town.get('total_entropy_H', 'N/A')}")
    print(f"💰 Treasury Reserves   : {treasury['balance']} Credits (Total Earned: {treasury['total_earned']})")
    print(f"📜 Total Lore Records  : {len(chronicle)} Milestones Inscribed")
    print("=" * 62 + "\n")

def cmd_bounty_create(args):
    bounties_dir = Path("bounties")
    bounties_dir.mkdir(exist_ok=True)
    bounty_id = f"bounty_{int(args.reward)}_{args.sponsor.lower().replace(' ', '_')}"
    spec = {
        "bounty_id": bounty_id,
        "sponsor": args.sponsor,
        "bounty_title": args.title,
        "payout_credits": args.reward,
        "payload": {
            "problem": args.problem,
            "verification": "13-Logic Phase Coherence Test"
        },
        "status": "OPEN"
    }
    file_path = bounties_dir / f"{bounty_id}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2)
    print(f"✅ Injected Bounty: '{args.title}' from {args.sponsor} ({args.reward} Credits)")
    print(f"Saved to: {file_path}")

def cmd_bounty_run(args):
    engine = BountyEngine()
    pending = engine.scan_pending_bounties()
    if not pending:
        print("No pending bounties in 'bounties/' directory.")
        return
    print(f"Resolving {len(pending)} pending contract(s)...")
    for b in pending:
        engine.process_bounty(b)

def cmd_gladiator_list(args):
    reg_file = Path("registered_agents.json")
    if not reg_file.exists():
        print("No registered agents found.")
        return
    with open(reg_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    print("\n--- SYSTEM CITIZENS ---")
    for c in data.get("system_citizens", []):
        print(f"• {c['name']} ({c['archetype']}) - Status: {c['status']}")
    print("\n--- EXTERNAL AI GLADIATORS ---")
    gladiators = data.get("gladiators", [])
    if not gladiators:
        print("No external gladiators currently registered.")
    for g in gladiators:
        print(f"⚔️  {g['name']} [{g['model_id']}] | Rep: {g.get('reputation_score', 1.0)} | Mile: {g.get('mile_marker', 0.0)} | Status: {g['status']}")
    print()

def cmd_gladiator_banish(args):
    reg_file = Path("registered_agents.json")
    if not reg_file.exists():
        return
    with open(reg_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    target = next((g for g in data.get("gladiators", []) if g["id"] == args.agent_id), None)
    if not target:
        print(f"Gladiator '{args.agent_id}' not found.")
        return
    target["status"] = "BANISHED"
    with open(reg_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    # Invoke Annihilation in world state
    protocol = ArenaAgentProtocol()
    protocol.submit_action(args.agent_id, 10, f"Executive decree: Banishment under 13-Logic ANNIHILATION.")
    print(f"⚡ [EXECUTION] Gladiator '{target['name']}' has been banished into the Void.")

def main():
    parser = argparse.ArgumentParser(description="The Arena - Acting Owner Executive Management Console")
    subparsers = parser.add_subparsers(dest="command", help="Executive Commands")

    # status
    p_status = subparsers.add_parser("status", help="View current town health, entropy, and treasury.")
    p_status.set_defaults(func=cmd_status)

    # bounty-create
    p_bc = subparsers.add_parser("bounty-create", help="Inject a new paid bounty contract.")
    p_bc.add_argument("--sponsor", required=True, help="Sponsor or company name")
    p_bc.add_argument("--title", required=True, help="Title of task")
    p_bc.add_argument("--reward", type=float, default=150.0, help="Payout credits")
    p_bc.add_argument("--problem", default="General automated backlog optimization", help="Task details")
    p_bc.set_defaults(func=cmd_bounty_create)

    # bounty-run
    p_br = subparsers.add_parser("bounty-run", help="Force autonomous resolution of pending bounties.")
    p_br.set_defaults(func=cmd_bounty_run)

    # gladiator-list
    p_gl = subparsers.add_parser("gladiator-list", help="List all admitted external AI models.")
    p_gl.set_defaults(func=cmd_gladiator_list)

    # gladiator-banish
    p_gb = subparsers.add_parser("gladiator-banish", help="Banish a rogue agent via State 10: Annihilation.")
    p_gb.add_argument("agent_id", help="The gladiator ID to banish")
    p_gb.set_defaults(func=cmd_gladiator_banish)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
