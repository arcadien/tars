# Manual test FUNC-MECH-JOINT-001 — the columns turn on their joints

Requirement: [FUNC-MECH-JOINT-001](../../requirements/functional.md#func-mech-joint-001). Manual test on the first
assembled robot (harness fitted, lids on), then after any change to the joints or the tube routes; add a line to
*Results* every time it is run.

## Equipment
- The assembled robot, switched off, cells out.
- A multimeter (continuity), the wiring guide (`hardware/tars4_harness.html`, housing pin-outs).

## Setup
1. Robot lying on its back on a soft cloth, columns aligned.
2. Continuity check P1 / P2 → every housing (as in the harness guide's last step): note any open wire.

## Steps
1. For each of the three joints in turn: hold one column, turn its neighbour by hand through the whole travel the
   model allows, both ways. Note any binding, notch or wobble (side play felt at the column's far end).
2. Turn each joint back and forth 20 times through its whole travel.
3. Redo the continuity check of the setup.

## Pass criteria
- Step 1: every joint turns through its travel without binding and without wobble.
- Step 3: the same continuity as in the setup (no wire opened by the turns), no wire visibly pulled at a tube end.

## Results
| Date | Commit / build | Left joint | Middle joint | Right joint | Continuity after 20 turns | Pass | By | Notes |
|---|---|---|---|---|---|---|---|---|
