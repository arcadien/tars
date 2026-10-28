# Bench test FUNC-POWER-SWITCH-002 — charging works the same with the switch off and on

Requirement: [FUNC-POWER-SWITCH-002](../../requirements/functional.md#func-power-switch-002). Manual test, run at bring-up step **3.9** ([bring-up.md](bring-up.md)); add a line to *Results* every time it is run.

## Equipment
- The assembled robot, cells **partly discharged** (3.6–3.9 V), firmware idle at boot.
- A multimeter (V range, and mA / 10 A ranges for currents).
- A 5 V ≥ 2 A USB charger and a micro-USB cable.

## Setup
1. Open the left leg's lid.
2. Unplug **X16** (right cell), so that the whole pack current goes through the meter, then **X12** (left cell). Join the two B− contacts of X12 with a short jumper. Put the meter (current range) in series in B+: **A socket on the board-side B+, COM on the cell-side B+**. A positive reading is current flowing **into** the cell (charge), a negative one current flowing out of it.

## Steps
1. SW1 off, plug the charger. After 1 min, read the cell current (I_off).
2. SW1 on; let the robot boot and sit idle. After 1 min, read the cell current (I_on).

## Pass criteria
- |I_on − I_off| ≤ 10 % of I_off.

## Results
| Date | Commit / build | I_off | I_on | Difference | Pass | By | Notes |
|---|---|---|---|---|---|---|---|
