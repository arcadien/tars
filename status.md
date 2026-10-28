# Branch test-schematic — requirement acceptance tests

Branch state file (CLAUDE.md, *Branches*): read it first when the branch is picked up again, keep it
current, answer the questions here.

## Goal
Audit finding 4: every validated requirement is tested, or listed in `audits/exclusions.yml` with a reason.

## State (2026-10-28)
- Schematic tests read from the KiCad project (kicad-cli XML netlist, `tests/conftest.py`): TECH-POWER CELL-001,
  PROTECT-002, GROUND-001, REG-001, DIST-001; PLAT-POWER CHARGE-001, HOTPLUG-001, REG-002, REG-003, DIST-001,
  MONITOR-001, DETECT-001, GATE-001; VSENSE-001 strict xfail (NPN not drawn yet).
- J1 (micro-USB charging socket) drawn in the schematic (`tars:usb_charging_socket`); kicad_sch_gen.py portable.
- Model tests (`tests/test_mechanical.py`): PLAT-MECH-CHARGEPORT-001, PLAT-MECH-PIVOT-001. Build: TECH-BUILD-ARTIFACTS-001.
- Manual test sheets: `tests/bench/<ID>.md` (bench and print, results table with notes), `tests/manual/` (process:
  TECH-BUILD-CHECKS-001). The bring-up order moved from the README to `tests/bench/bring-up.md`.
- `tests/test_requirements.py`: fails when a validated requirement has no test, sheet or exclusion; warns for the 13
  firmware requirements (pending until the first firmware test) and for sheets never run.

## To do
- Refactor: rename `usbb*` to `usb_charging_socket*` in `tars4.scad` (and the `usbb_z0` / `usbb_y0` geometry keys of
  `harness.py`, `hardware/measurements.md`), separate `refactor` commit, after this branch.
- Requirement PLAT-POWER-VSENSE-001: draw the NPN, then remove the xfail mark.

## Open questions
| # | Question | Answer |
|---|---|---|
| T1 | REG-001 "every 3V3 load pin is on the +3V3 net": the microSD reader (behind Q5) and the PIR (behind R21's RC filter) are not on +3V3 itself. Read as "fed from +3V3, directly or through one switch / filter part"? | |

## Next
Commits, push, PR #7 ready for review.
