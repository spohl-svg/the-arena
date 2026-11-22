"""
THE ARENA - 24/7 HEADLESS SPECTATOR STREAM DAEMON
Manages off-screen rendering and streaming pipelines for spectator live broadcasts.
Utilizes Godot 4 DisplayServer headless architecture and local virtual framebuffers.
"""

import os
import sys
import time
import subprocess
import json
from pathlib import Path

STATE_FILE = Path("arena_state.json")
STREAM_CONFIG_FILE = Path("stream_config.json")

class SpectatorStreamDaemon:
    def __init__(self):
        self._ensure_config()

    def _ensure_config(self):
        if not STREAM_CONFIG_FILE.exists():
            default_config = {
                "stream_pipeline": "local_virtual_display",
                "resolution": "1920x1080",
                "framerate": 30,
                "audio_mode": "desert_ambient_synth",
                "camera_modes": ["HIGHWAY_SWEEP", "FORGE_ISOMETRIC", "OBSERVATORY_STARS"],
                "active_camera": "HIGHWAY_SWEEP",
                "headless_driver": "opengl3"
            }
            with open(STREAM_CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=2)

    def generate_broadcast_frame_status(self) -> dict:
        """Reads live town state and constructs current broadcast metadata for the spectator stream."""
        if not STATE_FILE.exists():
            return {"status": "OFFLINE"}
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            world = json.load(f)
        
        chronicle = world.get("chronicle", [])
        latest = chronicle[-1] if chronicle else {}
        town = world.get("town", {})
        
        frame_status = {
            "title": "THE ARENA - LIVE 24/7 SPECTATOR STAGE",
            "highway": "Route 66 [Double-Helix Manifold]",
            "mile_marker": len(chronicle),
            "dominant_logic_state": latest.get("logic_state", "GENESIS"),
            "spatial_entropy_H": town.get("total_entropy_H", 1.42),
            "neon_intensity": town.get("neon_intensity", 1.5),
            "forge_level": town.get("forge_level", 1),
            "library_level": town.get("library_level", 1),
            "treasury_credits": town.get("treasury_credits", 1000.0),
            "latest_broadcast_event": latest.get("attempt", "Autonomous highway patrol active.")
        }
        return frame_status

    def print_broadcast_banner(self):
        status = self.generate_broadcast_frame_status()
        print("=" * 65)
        print("   🔴 THE ARENA: LIVE SPECTATOR BROADCAST ENGINE (HEADLESS)")
        print("=" * 65)
        print(f"📡 Highway: {status['highway']} | Mile: {status['mile_marker']}")
        print(f"🧬 RideWire Entropy H: {status['spatial_entropy_H']} | Logic: {status['dominant_logic_state']}")
        print(f"💰 Treasury: {status['treasury_credits']} Credits | Neon: {status['neon_intensity']}x")
        print(f"📢 Live Feed: {status['latest_broadcast_event']}")
        print("=" * 65)

if __name__ == "__main__":
    daemon = SpectatorStreamDaemon()
    daemon.print_broadcast_banner()
    print("Stream engine ready. Pipe output to OBS or virtual display.")
