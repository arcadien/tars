# Branch mech-usb-heel — charge port at the heel

Branch state file (CLAUDE.md, *Branches*): read it first when the branch is picked up again, keep it
current, answer the questions here.

## Goal
Move the micro-USB charge port (J1) from under the left foot to its heel, so TARS charges standing up.

## State (2026-10-28)
- Requirements validated and committed: [FUNC-POWER-CHARGE-001](requirements/functional.md#func-power-charge-001)
  (port on the heel, reachable standing), [PLAT-POWER-CHARGE-001](requirements/platform.md#plat-power-charge-001)
  (breakout facing backwards through the lid), [PLAT-MECH-CHARGEPORT-001](requirements/platform.md#plat-mech-chargeport-001)
  (geometry, option A: breakout on the outer side wall).
- Model done (`feat(PLAT-MECH-CHARGEPORT-001)`): breakout standing against the outer side wall, bottom block + top rail
  with edge grooves, front stop in two tabs, back edge against the lid (pull-out stop), receptacle through a notch at
  the bottom of the lid, centre 10.3 above the floor; floor opening removed; geometry checks in `tars4.scad`.
- Regenerated: STLs, renders (+ `renders/tars4_heel_back.png`, `renders/tars4_heel_open.png`), harness guide (J1
  position), both Orca projects (meshes only). README, `hardware/measurements.md`, `open_questions.md` (CP1) updated.
- Tight spot: receptacle 0.755 from the switch frame (x), checked by the model.
- M2 / M3 measured and folded in (2026-10-28): `usbb_out` 1.1, `usbb_rec` 7.85 × 2.47 → lid notch 8.45 × 3.07 (bottom
  6.0 above the floor), mouth 0.7 inside the back face; CP1 removed from `open_questions.md`.
- Toolchain fixes for Windows found on the way: `build4.sh` passes `cygpath -m` paths in the render includes,
  `boards.py` / `harness.py` read and write their text files in UTF-8; `connectors.scad` (XH() for the renders)
  now lives next to `tars4.scad`.

## Open questions
| # | Question | Answer |
|---|---|---|
| M1 | Breakout orientation: receptacle on a 14.3 side, the 16 towards the back? | yes (2026-10-28) |
| M2 | `usbb_out`: receptacle mouth past the PCB's back edge (modelled 1.0; ≥ 0.8 needed, else the PCB goes through the lid) | ~1.1, hard to read (2026-10-28); drives no printed geometry |
| M3 | `usbb_rec`: receptacle shell width × height above the PCB (modelled 7.5 × 2.6) | 7.85 × 2.47 (2026-10-28) |

## Merge condition
Measurements folded in. Left: `make check` clean, Orca refresh (warn Aurelien first), remove this file, PR to main.
