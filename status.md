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

## Next step
Test committed (xfail), then, then the optimiser in `tools/boards.py`.
