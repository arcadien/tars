# Branch harness-board-layout

## Goal
Minimise the assembly effort of the hand-wired boards (P1, P2, P3 carrier, P4 power-path): fewer solder bridges,
jumpers, buses and strip cuts. Board size may grow within the room the model leaves.

## State
- Draft requirement [TECH-HARNESS-BOARDS-001](requirements/technical.md#tech-harness-boards-001), waiting for review.
- KiCadRoutingTools looked at and set aside: it autoroutes copper tracks on `.kicad_pcb`, it knows nothing of
  stripboard strips, cuts or bridges.

## Baseline (score: bridge 1, cut 1, jumper 2, bus / link 2)
| Board | Grid | Bridges (pairs) | Jumpers | Bus / link | Cuts |
|---|---|---|---|---|---|
| P3 carrier | 10 × 13 pads | 13 groups | 4 | 1 | 0 |
| P1 | 9 × 12 strips | 0 | 0 | 1 | 0 |
| P2 | 9 × 12 strips | 0 | 1 | 0 | 2 |
| P4 power | 10 × 8 pads | 12 groups | 0 | 1 | 0 |

## Open questions
- Score weights (bridge 1, cut 1, jumper 2, bus / link 2): OK?
- Max size per board: from the model (hub column width, power-leg grooves) — to compute.

## Next step
Validate the requirement, then the test (local minimum), then the optimiser in `tools/boards.py`.
