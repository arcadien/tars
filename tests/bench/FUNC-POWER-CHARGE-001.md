# Bench test FUNC-POWER-CHARGE-001 — battery charges from the heel port, robot standing

Requirement: [FUNC-POWER-CHARGE-001](../../requirements/functional.md#func-power-charge-001). Manual test, run at bring-up step **3.9** ([bring-up.md](bring-up.md)); add a line to *Results* every time it is run.

## Equipment
- The assembled robot, both cells fitted and **partly discharged** (3.5–3.9 V at B+, switch off).
- A 5 V ≥ 2 A USB charger and a micro-USB cable.
- A multimeter (V range, and mA / 10 A ranges for currents).
- A flat table.

## Setup
1. Switch the robot off (SW1, floor of the left leg). Open the left leg's lid.
2. Unplug **X16** (right cell), so that the whole pack current goes through the meter, then **X12** (left cell). Join the two B− contacts of X12 with a short jumper. Put the meter on its **10 A socket** (the mA socket fuse blows at 0.5 A) in series in B+: **A socket on the board-side B+, COM on the cell-side B+**. A positive reading is current flowing **into** the cell (charge), a negative one current flowing out of it.
3. Close the lid as far as the meter leads allow. Stand the robot upright on its feet on the table.

## Steps
1. Plug the micro-USB cable into the charge port at the **heel of the left leg**, horizontally from behind, without lifting or tilting the robot. Plug the charger into the mains.
2. After 10 s, read the current into the cell. After 5 min, read the cell voltage (meter on V, across the cell-side X12 contacts) and compare with the value before charging.
3. Check that the robot still stands, the cable resting on the table.
4. Lay the robot face down: check that the cable can be plugged in the same way.

## Pass criteria
- Step 2: positive current (into the cell), and the cell voltage after 5 min is higher than before.
- Step 3: the robot stands with the cable plugged in.
- Step 4: the port is reachable lying face down.

## Results
| Date | Commit / build | Cell V before → after 5 min | Current | Standing | Face down | Pass | By | Notes |
|---|---|---|---|---|---|---|---|---|
