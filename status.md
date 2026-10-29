# Branch hw-vsense — VSYS sense (PLAT-POWER-VSENSE-001) drawn and wired

Branch state file (CLAUDE.md, *Branches*): read it first when the branch is picked up again, keep it
current, answer the questions here. Based on `test-schematic`; main (PR #7) merged in.

## Goal
Implement PLAT-POWER-VSENSE-001: an NPN level detector tells GPIO37 whether VSYS is up.

## State (2026-10-29)
- Option B chosen: R23 1 MΩ soldered in line in the harness at the power-path board end (VSYS hole D4, bridged to D3),
  so the wire through the left tube carries VSYS only behind 1 MΩ; R24 1 MΩ and Q4 BC547B standing on the carrier
  (F9–H10), collector bridged to IO37 (I10). P4 has no room for two more lying resistors (search: 6 runs, at most 3–4
  fit), and a 10 × 9 P4 leaves 4.76 mm of front wire corridor (< 6 mm rule).
- X14 becomes a JST-XH 4 (4th contact VSENSE_B); too long for the front parking row next to X10, it gets its own row
  in front, centred (model clean). Left tube: 14 wires.
- Schematic: Q4 / R23 / R24 block, IO37 on VSENSE; netlist OK (51 nets), ERC clean. The VSENSE test passes (xfail removed).
- Tools: boards.py knows TO-92 parts (kind T) and resistors in line in a wire (`{'inline': (ref, value, net after)}`);
  harness.py notes them in the guide.

## Open questions
| # | Question | Answer |
|---|---|---|
| V1 | VSENSE_B wire colour: brown 30 AWG with 1 black ring (analog like VBAT/2, the ring tells them apart in X14)? | yes (2026-10-29) |
| V2 | PLAT-POWER-VSENSE-001 still says "Hardware change, not yet in kicad_sch_gen.py, the boards or the wiring": replace by "R23 in line in the harness at the power-path board, R24 and Q4 on the carrier" (req change, to validate)? | yes, committed (2026-10-29) |
| V3 | Schematic review by Aurelien | done (2026-10-29) |

## Next
PR to main; after the `docs-drop-schematic-html` merge, add Q4 / R23 / R24 to `hardware/design_notes.md`.
