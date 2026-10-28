# Branch test-schematic — requirement acceptance tests on the KiCad schematic

Branch state file (CLAUDE.md, *Branches*): read it first when the branch is picked up again, keep it
current, answer the questions here.

## Goal
Audit finding 4: the 17 validated requirements whose acceptance says "pytest on the schematic" get their tests,
read from the KiCad project itself (kicad-cli XML netlist), not from tools/kicad_sch_gen.py.

## State (2026-10-28)
- tests/conftest.py: netlist exported once per run, nets found through their pins (generated names change).
- TECH-POWER: CELL-001, PROTECT-002, GROUND-001, REG-001, DIST-001 (also reads the boards.py / harness.py wires).
- Each test checked against a deliberately broken netlist (TARS_NETLIST): it fails, the others pass.
- Left: the 12 PLAT requirements (requirements/platform.md), wiring into the erc stage and CI.

## Open questions
| # | Question | Answer |
|---|---|---|
| T1 | REG-001 "every 3V3 load pin is on the +3V3 net": the microSD reader (behind Q5) and the PIR (behind R21's RC filter) are not on +3V3 itself. Read as "fed from +3V3, directly or through one switch / filter part"? | |

## Next
PLAT tests with Aurelien, then wire pytest into the erc stage (pre-commit) and CI.
