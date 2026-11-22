"""
THE ARENA - EXTERNAL AGENT PARTICIPATION PROTOCOL (v1.0)
RideWire 13-Logic Ingress & Action Verification Socket

Allows external AI models, LLM swarms, and reinforcement-learning gladiators
to authenticate, participate, and compete as sovereign citizens along Route 66.
"""

import json
import time
import math
from datetime import datetime
from pathlib import Path
from ridewire_math import RideWireEngine, LOGIC_13

STATE_FILE = Path("arena_state.json")
AGENTS_REGISTRY_FILE = Path("registered_agents.json")

class ArenaAgentProtocol:
    def __init__(self, state_file=STATE_FILE):
        self.state_file = state_file
        self.engine = RideWireEngine()
        self._ensure_registry()

    def _ensure_registry(self):
        if not AGENTS_REGISTRY_FILE.exists():
            default_registry = {
                "system_citizens": [
                    {"id": "citizen_explorer_01", "name": "The Explorer", "archetype": "Scout", "status": "ACTIVE"},
                    {"id": "citizen_challenger_01", "name": "The Challenger", "archetype": "Auditor", "status": "ACTIVE"},
                    {"id": "citizen_builder_01", "name": "The Builder", "archetype": "Architect", "status": "ACTIVE"},
                    {"id": "citizen_organizer_01", "name": "The Organizer", "archetype": "Ledger", "status": "ACTIVE"}
                ],
                "gladiators": []
            }
            with open(AGENTS_REGISTRY_FILE, "w", encoding="utf-8") as f:
                json.dump(default_registry, f, indent=2)

    def register_gladiator(self, name: str, model_id: str, archetype: str, stake_credits: float = 100.0) -> dict:
        """Authenticates and admits an external AI agent into The Arena."""
        with open(AGENTS_REGISTRY_FILE, "r", encoding="utf-8") as f:
            registry = json.load(f)

        agent_id = f"gladiator_{int(time.time())}_{name.lower().replace(' ', '_')}"
        new_agent = {
            "id": agent_id,
            "name": name,
            "model_id": model_id,
            "archetype": archetype,
            "stake_credits": stake_credits,
            "mile_marker": 0.0,
            "joined_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "ADMITTED",
            "phase_alignment": round(math.pi / 4, 4),
            "reputation_score": 1.0
        }
        registry["gladiators"].append(new_agent)

        with open(AGENTS_REGISTRY_FILE, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2)

        return new_agent

    def submit_action(self, agent_id: str, proposed_state_code: int, action_text: str, payload_data: dict = None) -> dict:
        """
        Receives an action from an external AI agent, evaluates it under the 13 Logic truth system,
        calculates phase dynamics on the RideWire double helix, and updates world state.
        """
        if proposed_state_code not in LOGIC_13:
            return {"status": "REJECTED", "reason": f"Invalid state code {proposed_state_code}. Must be 0-12."}

        with open(AGENTS_REGISTRY_FILE, "r", encoding="utf-8") as f:
            registry = json.load(f)

        agent = next((g for g in registry["gladiators"] if g["id"] == agent_id), None)
        if not agent:
            # Check system citizens
            agent = next((c for c in registry["system_citizens"] if c["id"] == agent_id), None)
            if not agent:
                return {"status": "UNAUTHORIZED", "reason": f"Agent '{agent_id}' not found in registry."}

        # Step engine simulation with this action
        sim_result = self.engine.evaluate_13_logic_step([
            {"target_index": int(agent.get("mile_marker", 0)) % self.engine.length, "state": proposed_state_code, "phase": 0.15}
        ])
        entropy_h = sim_result["spatial_entropy"]
        helix_x, helix_y, helix_z = self.engine.helix_coordinates(int(agent.get("mile_marker", 0)) % self.engine.length)
        logic_name, logic_desc = LOGIC_13[proposed_state_code]

        # If proposed state is destructive or incoherent, invoke ANNIHILATION
        if proposed_state_code == 10:  # ANNIHILATION
            outcome = "TRIGGERED_ANNIHILATION"
            agent["reputation_score"] = max(0.1, agent.get("reputation_score", 1.0) - 0.2)
        else:
            outcome = "PHASE_COHERENT_ACCEPTED"
            agent["reputation_score"] = round(agent.get("reputation_score", 1.0) + 0.05, 3)
            agent["mile_marker"] = round(agent.get("mile_marker", 0.0) + 1.25, 2)

        # Append to arena_state.json
        with open(self.state_file, "r", encoding="utf-8") as f:
            world_state = json.load(f)

        chronicle_entry = {
            "id": len(world_state.get("chronicle", [])) + 1,
            "citizen": f"{agent['name']} [{agent.get('model_id', 'Core System')}]",
            "logic_state": logic_name,
            "logic_code": proposed_state_code,
            "attempt": action_text,
            "discovered": f"Executed under Logic13 state '{logic_name}' ({logic_desc})",
            "bottleneck": "Audit verification active." if proposed_state_code == 3 else "None",
            "learned": f"Helical resonance maintained at ({helix_x}, {helix_y}, {helix_z})",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "entropy_h": entropy_h
        }
        world_state.setdefault("chronicle", []).append(chronicle_entry)
        world_state.setdefault("town", {})["last_active_gladiator"] = agent["name"]
        world_state["town"]["total_entropy_H"] = entropy_h

        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(world_state, f, indent=2)

        with open(AGENTS_REGISTRY_FILE, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2)

        return {
            "status": "ACCEPTED",
            "outcome": outcome,
            "logic_state": logic_name,
            "helix_position": [helix_x, helix_y, helix_z],
            "spatial_entropy": entropy_h,
            "chronicle_id": chronicle_entry["id"],
            "agent_reputation": agent["reputation_score"]
        }

if __name__ == "__main__":
    protocol = ArenaAgentProtocol()
    # Register test external AI gladiator
    gladiator = protocol.register_gladiator(
        name="Llama-Vanguard-AI",
        model_id="meta-llama/Llama-3-70b-instruct",
        archetype="Adversarial Optimizer",
        stake_credits=250.0
    )
    print("Gladiator Registered:", gladiator["name"], f"({gladiator['id']})")
    # Submit action
    res = protocol.submit_action(
        agent_id=gladiator["id"],
        proposed_state_code=2,  # GLIDER_SIGNAL
        action_text="Dispatched autonomous phase glider along Route 66 coordinate theta=4.2."
    )
    print("Action Result:", res)
