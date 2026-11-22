<!-- THE ARENA — Search-Space Template.
Every PR submitted by The Builder must populate this template in full.
If the hypothesis or ruled-out paths are blank, The Challenger immediately
issues a rejection. -->

### 1. The Hypothesis & Objective
- **Target Issue:** Resolves #[issue_number]
- **The Problem:** [What structural bug, phase drift, or feature in The Arena is being addressed?]
- **Proposed Mechanism:** [Why does this specific code change solve it without causing regressions?]

### 2. Retrieved Memory & Precedents
- **Foundational References:** [e.g., the GitHub-native agent workflow paper, Archimedean lattice phase coupling, Godot 4.3 single-thread export documentation]
- **Chronicle Precedent:** [Which Chronicle entry or past git commit provides the baseline?]

### 3. Ruled-Out Paths & Historical Trials
- **Failed / Rejected Approaches:** [What potential solutions were considered and eliminated?]
- **Why Avoided:** [e.g., Avoided GitHub REST API to prevent token bloat; avoided multi-threaded Godot Web export due to CORS cross-origin isolation issues on itch.io]

### 4. Bounded Search Space
- **Files Modified:** [Explicit list of permitted files]
- **Strict Out-of-Bounds:** [Files that must NOT be touched, e.g., core agent IDs, physics ticks, cost parameters]

### 5. Verification & Audit Trail
- **CLI Compilation Check:** `python3 -m py_compile [files]` -> [PASS/FAIL]
- **Simulation Invariant Check:** [Describe verification of phase coupling, memory leak check, or Godot node parity]
- **Ledger Impact:** Machine Cost Delta: $0.00 | Resource Footprint: [e2-micro memory %]
