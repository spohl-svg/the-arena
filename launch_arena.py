import os
import sys
import time
import shutil
import subprocess
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
RUNNER_SCRIPT = PROJECT_DIR / "arena_runner.py"

def find_godot():
    """Look for Godot in PATH or in the current directory."""
    # 1. Check standard PATH names
    for name in ["godot", "godot4", "Godot", "Godot4"]:
        path = shutil.which(name)
        if path:
            return path

    # 2. Check local project directory for standalone godot binaries / .exe
    candidates = list(PROJECT_DIR.glob("godot*")) + list(PROJECT_DIR.glob("Godot*"))
    for cand in candidates:
        if cand.is_file() and (cand.suffix.lower() in [".exe", ""] or os.access(cand, os.X_OK)):
            return str(cand)

    return None

def main():
    print("=" * 65)
    print("        WELCOME TO THE ARENA - 1-CLICK LAUNCHER")
    print("   Starting Citizen Autonomous Daemon & Godot World View")
    print("=" * 65)
    print(f"Working Directory: {PROJECT_DIR}\n")

    if not RUNNER_SCRIPT.exists():
        print(f"Error: {RUNNER_SCRIPT} not found!")
        sys.exit(1)

    # 1. Start the Background Citizen Daemon
    print(">> Launching autonomous Citizen Daemon (arena_runner.py)...")
    runner_cmd = [sys.executable, str(RUNNER_SCRIPT)]
    if "--test" in sys.argv:
        runner_cmd.append("--test")

    runner_proc = subprocess.Popen(
        runner_cmd,
        cwd=str(PROJECT_DIR)
    )

    # Give the runner a moment to initialize state
    time.sleep(1.5)

    # 2. Check for Godot executable
    godot_bin = find_godot()
    godot_proc = None

    if godot_bin:
        print(f">> Found Godot executable at: {godot_bin}")
        print(">> Launching Godot 3D World View...")
        try:
            godot_proc = subprocess.Popen(
                [godot_bin, "--path", str(PROJECT_DIR)],
                cwd=str(PROJECT_DIR)
            )
        except Exception as e:
            print(f"Warning: Could not launch Godot automatically: {e}")
    else:
        print("\n" + "*" * 65)
        print(">> Autonomous Citizen Daemon is running smoothly in the background!")
        print(">> Next step to open the 3D visual world:")
        print("   1. Open Godot 4")
        print("   2. Click 'Import' and select 'project.godot' in this folder")
        print("   3. Press Play (F5) to watch your town live.")
        print("   (Tip: You can also copy your 'godot.exe' directly into this")
        print("    folder, and this launcher will open the game window automatically!)")
        print("*" * 65 + "\n")

    print("\nPress Ctrl+C at any time in this window to stop all processes.\n")

    try:
        while True:
            # Check if background runner exited
            if runner_proc.poll() is not None:
                print("\n[Notice] Citizen Daemon finished or stopped.")
                break
            if godot_proc and godot_proc.poll() is not None:
                print("\n[Notice] Godot client was closed.")
                # We keep running daemon unless user interrupts, or prompt
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping The Arena...")
    finally:
        if runner_proc.poll() is None:
            runner_proc.terminate()
        if godot_proc and godot_proc.poll() is None:
            godot_proc.terminate()
        print("All processes safely stopped. Progress preserved in arena_state.json.")

if __name__ == "__main__":
    main()
