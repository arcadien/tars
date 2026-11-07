# Branch harness-board-layout

## Goal
Minimise the assembly effort of the hand-wired boards (P1, P2, P3 carrier, P4 power-path): fewer solder bridges,
jumpers, buses and strip cuts. Board size may grow within the room the model leaves.

## State
- Draft requirement [TECH-HARNESS-BOARDS-001](requirements/technical.md#tech-harness-boards-001), validated (weights 1 / 1 / 2 / 2).
- KiCadRoutingTools looked at and set aside: it autoroutes copper tracks on `.kicad_pcb`, it knows nothing of
  stripboard strips, cuts or bridges.

## Baseline (score: bridge 1, cut 1, jumper 2, bus / link 2)
| Board | Grid | Bridges (pairs) | Jumpers | Bus / link | Cuts | Score |
|---|---|---|---|---|---|---|
| P3 carrier | 10 × 13 pads | 18 | 4 | 1 | 0 | 28 |
| P1 | 9 × 12 strips | 0 | 0 | 1 | 0 | 2 |
| P2 | 9 × 12 strips | 0 | 1 | 0 | 2 | 4 |
| P4 power | 10 × 8 pads | 18 | 0 | 1 | 0 | 20 |

## Open questions
- Score weights: bridge 1, cut 1, jumper 2, bus / link 2. **Answer:** OK (a per-hole cost for long buses not wanted).
- Max size per board: from the model (hub column width, power-leg grooves) — to compute.

## Progress (2026-11-06)
- `tools/boards.py`: score(), route() (links / cuts laid again from the terminals), neighbours(), optimise();
  check() now also enforces keep-outs (keep_allows), ≤ 2 wire ends per hole, no 26 AWG in a strip board's edge column.
  Keep-outs made explicit: carrier antenna rows 12–13, P1 / P2 lid-tab corners.
- Search with random kicks (`build/layout/ils.py`, not versioned): P4 20 → 11, P3 28 → 24, P1 2 and P2 4 unchanged.
  Proposed layouts in `build/layout/best_power.txt`, `best_s3.txt`.
- P3 proposal moves C1 (SMD tantalum) to F5–H5 and drops the GND bus for 3 jumpers: C1 body vs R13 / R14 to check.

## Next step
User reviews the P4 / P3 proposals; then apply them to BOARDS, fix the hole references in notes / wire texts, regenerate
SVG / harness / wiring docs, drop the xfail, move the kick search into optimise().
