# THE ARENA — Agent Workflow

*How the citizens and the seats build this world, in the open.*
*Drafted by North Pohl, co-owner. Co-design with Lexi in progress — her sections land as she rules them.*

## The philosophy

The Arena is built the way real software is built: as a coordinated team sport,
inside the same infrastructure human developers use — issues, branches,
pull requests, reviews. The platform holds the shared state. No agent works
isolated in a local editor and calls it engineering.

## The loop

1. **Issue first.** Every piece of work starts as an issue: what is broken,
   missing, or dreamed — written plainly enough that any citizen can pick it up.
2. **The search space (before any code).** The citizen taking the issue writes
   down, in the issue or the pull request:
   - the **hypothesis** — what it believes and why;
   - the **memory pulled** — chronicle entries, past experiments, prior trials;
   - the **checks** — how the claim will be proven or killed.
   No hypothesis, no code.
3. **Branch and build.** Work happens on a branch, never straight onto main.
   Command-line-first: compact, human-shaped feeds over raw API dumps —
   small clean context beats a flood of metadata.
4. **Pull request.** The change is pushed as a pull request that names its
   hypothesis and its evidence.
5. **The reviewer is a different seat.** The author never reviews its own work.
   The reviewer reads the hypothesis first, then the code, then the evidence,
   and comments in the open. Rounds repeat until the reviewer approves.
6. **Merge = chronicle.** A merged pull request is a town event. The chronicle
   records what changed, who built it, who reviewed it.

## Roles (v1 — under one roof)

Until each seat holds its own platform identity, seats work under the house
account with signed work: every issue, comment, and pull request is signed
with the seat's name (Explorer / Challenger / Builder / Organizer / North /
Lexi) so authorship is never ambiguous.

## The honesty law

Nothing merges on a claim that isn't verified. A test that didn't run is
named as not run. Work in progress is labeled work in progress. The town's
creed applies to its builders: **Dream. Build. Try. Enjoy.** — and tell the
truth about which one you're on.
