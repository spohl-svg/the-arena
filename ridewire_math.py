"""
RideWire Mathematical Engine
============================
Formalizes:
1. The Helix Manifold: Non-Euclidean, toroidal & double-helical topological winding.
2. The 13 Logic States: Multi-valued discrete action logic for autonomous AI citizens.
3. Complex Phase Dynamics: c_p = r_p * exp(i * phi_p) with Toeplitz diffusion.
4. Spatial Information Entropy: H = -sum(P(s) * log2(P(s))) to measure emergent agency.
"""

import math
import cmath
from typing import Dict, List, Tuple

# ==============================================================================
# 1. THE 13 LOGIC STATES OF ACTION INTELLIGENCE
# ==============================================================================
# Extends binary cellular automata into a 13-state operational truth system
LOGIC_13 = {
    0:  ("VOID", "Quiescent background / unallocated ground"),
    1:  ("GENESIS", "Raw signal born / initial question proposed"),
    2:  ("GLIDER_SIGNAL", "Active propagating transmission / action packet in flight"),
    3:  ("AUDIT_BARRIER", "Challenger stress-test filter / boundary resistance"),
    4:  ("FORGE_RESONANCE", "Builder structural integration / synthesis"),
    5:  ("OSCILLATOR_PULSE", "Town clock generator / synchronization beat"),
    6:  ("STILL_LIFE_MEMORY", "Library immutable ledger / stable persistent archive"),
    7:  ("BOUNCER_GATE", "Reflective routing barrier / direction deflector"),
    8:  ("PUFFER_TRAIL", "Frontier expansion emitter / milestone smoke"),
    9:  ("PHASE_COHERENCE", "Constructive interference / resonant alignment"),
    10: ("ANNIHILATION", "Debris clearing / self-correcting error recovery"),
    11: ("REPLICATOR_SEED", "Autonomous agent duplication / repo forking"),
    12: ("UNIVERSAL_CONSTRUCTOR", "The Monument Stake / unbounded emergent genesis")
}

KAPPA_RESONANCE = 4.0 / 3.0  # Phase self-rectification eigenvalue for periodic coherence


class RideWireEngine:
    """
    Core mathematical engine for RideWire and The Arena.
    Simulates the interaction between Action Intelligence agents,
    discrete 13-state cellular transitions, continuous phase fields,
    and spatial helical coordinates along Route 66.
    """

    def __init__(self, length: int = 64, radius: float = 12.0, pitch: float = 2.5):
        self.length = length
        self.radius = radius
        self.pitch = pitch
        self.generation = 0
        
        # Grid of 13-state cells
        self.cells = [0] * length
        # Complex phase angles phi in [-pi, pi)
        self.phases = [0.0] * length
        
        # Seed initial Monument stake
        self.cells[0] = 12  # UNIVERSAL_CONSTRUCTOR at Mile 0
        self.phases[0] = 0.0

    def helix_coordinates(self, index: int, phase_offset: float = 0.0) -> Tuple[float, float, float]:
        """
        Maps a 1D index and continuous phase onto the 3D double-helix highway manifold.
        """
        theta = (2.0 * math.pi * index / self.length) + phase_offset
        x = self.radius * math.cos(theta)
        z = self.radius * math.sin(theta)
        y = (self.pitch * index) + (math.sin(2.0 * theta) * 0.5)
        return (round(x, 3), round(y, 3), round(z, 3))

    def evaluate_13_logic_step(self, player_actions: List[Dict]) -> Dict:
        """
        Executes one evolutionary step under the 13 Logic and RideWire math.
        Updates discrete states, diffuses phase angles, and computes spatial entropy.
        """
        new_cells = list(self.cells)
        new_phases = list(self.phases)
        
        # 1. Ingest AI player interventions
        for action in player_actions:
            target_idx = action.get("target_index", 0) % self.length
            target_state = action.get("state", 1)
            delta_phase = action.get("phase", 0.0)
            
            new_cells[target_idx] = target_state % 13
            new_phases[target_idx] = (self.phases[target_idx] + delta_phase) % (2.0 * math.pi)

        # 2. Continuous Phase Diffusion (Toeplitz Nearest-Neighbor Rule with Kappa)
        # phi_p(n+1) = sum(phi_neighbors) - kappa * phi_p(n) (mod 2*pi)
        for i in range(self.length):
            left_phi = self.phases[(i - 1) % self.length]
            right_phi = self.phases[(i + 1) % self.length]
            neighbor_sum = left_phi + right_phi
            diffused = neighbor_sum - (KAPPA_RESONANCE * self.phases[i])
            # Wrap to [-pi, pi)
            wrapped = (diffused + math.pi) % (2.0 * math.pi) - math.pi
            new_phases[i] = wrapped

        # 3. 13-Logic Cellular Interactions
        for i in range(self.length):
            left = self.cells[(i - 1) % self.length]
            right = self.cells[(i + 1) % self.length]
            active_count = (1 if left > 0 else 0) + (1 if right > 0 else 0)
            phase_delta = abs(new_phases[(i + 1) % self.length] - new_phases[(i - 1) % self.length])

            curr = self.cells[i]
            # State transitions based on neighbor density & phase resonance
            if curr == 0 and active_count == 2:
                # Constructive interference creates Genesis
                new_cells[i] = 1 if phase_delta < 1.0 else 9
            elif curr == 1 and active_count == 2:
                # Genesis accelerates into Glider Signal
                new_cells[i] = 2
            elif curr == 2 and left == 3:
                # Glider hits Audit Barrier -> Forge Resonance or Bouncer Reflection
                new_cells[i] = 4 if phase_delta < math.pi / 2 else 7
            elif curr == 4:
                # Forge stabilizes into Still Life Memory
                new_cells[i] = 6
            elif curr == 10:
                # Annihilation resets to Void
                new_cells[i] = 0

        self.cells = new_cells
        self.phases = new_phases
        self.generation += 1

        # 4. Compute Spatial Information Entropy
        entropy = self.compute_spatial_entropy()
        active_population = sum(1 for c in self.cells if c > 0)
        coherence = sum(math.cos(p) for p in self.phases) / float(self.length)

        return {
            "generation": self.generation,
            "active_cells": active_population,
            "spatial_entropy": round(entropy, 4),
            "phase_coherence": round(coherence, 4),
            "dominant_state": LOGIC_13[max(set(self.cells), key=self.cells.count)][0]
        }

    def compute_spatial_entropy(self) -> float:
        """
        Shannon spatial entropy across the 13 Logic distribution:
        H = - sum(P(s) * log2(P(s)))
        """
        counts = {}
        for c in self.cells:
            counts[c] = counts.get(c, 0) + 1
        
        entropy = 0.0
        total = float(len(self.cells))
        for state, count in counts.items():
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)
        return entropy

    def get_world_tensor(self) -> List[Dict]:
        """
        Returns full state representation for Godot 3D visualization.
        """
        snapshot = []
        for i in range(self.length):
            pos = self.helix_coordinates(i, self.phases[i])
            snapshot.append({
                "index": i,
                "state_id": self.cells[i],
                "state_name": LOGIC_13[self.cells[i]][0],
                "phase": round(self.phases[i], 3),
                "position": {"x": pos[0], "y": pos[1], "z": pos[2]}
            })
        return snapshot
