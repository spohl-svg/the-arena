# STATUS BOARD — The Witness Door

`status_board.py` builds **one page a witness can open on a phone** and see
that the town is alive: `status.html`.

It is the **Issue #1 first build** — the successor to the public chronicle
feed (`chronicle_feed.py`). The feed showed the latest chronicle lines;
the Witness Door shows the **whole town** on a single self-contained page:

- the town's name and creed header, with its live neon sign text
- the **two-number ledger line** — machine cost (estimate) vs world earned
  (verified receipts only), computed from `arena_ledger.json` exactly the
  way `arena_ledger.py` computes it
- town vitals: chronicle length (the Mile), citizens, buildings, districts,
  treasury credits (in-game)
- the **citizen roster grouped by district** — name, seat, home building,
  shifts completed, and each apprentice's mentor
- **building levels** with district and purpose
- the **latest 25 chronicle entries** — citizen, attempt, discovered,
  learned, timestamp

## How it runs

- **Where:** on the VM, in `/opt/arena`, beside the daemon — the same
  directory as `arena_runner.py`, `arena_state.json`, and
  `arena_ledger.json`. It reads those two JSON files from its own
  directory and writes `status.html` next to them. Python standard
  library only; no installs, no external assets, no server logic in the
  page itself.
- **When:** regenerate **every N cycles or on a timer** — the board is a
  static snapshot, so freshness is set by how often it is rebuilt. Two
  easy wirings:
  - call `build_status()` from the runner at a cycle interval (e.g.
    every 50 cycles), or
  - a cron/systemd timer on the VM, e.g. every 15 minutes:
    `cd /opt/arena && python3 status_board.py`
- **Serving:** the file is fully self-contained (inline styling, no
  external requests), so any static host or a tiny HTTP server on the VM
  can serve it as-is. One bookmark on Stephanie's phone is the whole
  interface — no app, no sign-in, no spreadsheet.

## Honesty notes

- Machine cost is labeled an **estimate** (VM list rate × uptime), the
  same basis as the daemon's `[ARENA LEDGER]` heartbeat line.
- World earned shows **verified receipts only** — inflow is recorded in
  the ledger only when a real sale lands. Nothing is invented.
- Treasury credits are **in-game** and are labeled as such on the page.
