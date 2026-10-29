# Bench test FUNC-POWER-SWITCH-001 — the switch turns the system rail off

Requirement: [FUNC-POWER-SWITCH-001](../../requirements/functional.md#func-power-switch-001). Manual test, run at bring-up step **3.2** ([bring-up.md](bring-up.md)); add a line to *Results* every time it is run.

## Equipment
- A bench supply, 3.7 V, current limit 300 mA (stands in for the cells).
- A multimeter (V range, and mA / 10 A ranges for currents).
- A 5 V ≥ 2 A USB charger and a micro-USB cable.

## Setup
1. Power block on the bench, nothing on the 3V3. Bench supply on the TP4056 B+ / B− pads.
2. Meter (V) across VSYS and GND. VSYS and GND are reached at the X13 contacts of the power block (VSYS, GND amp).

## Steps
1. SW1 on: note VSYS (≈ the supply voltage: proves the wiring).
2. SW1 off, battery only: note VSYS.
3. SW1 off, plug the charger into the charge port: note VSYS.

## Pass criteria
- Steps 2 and 3: VSYS < 0.1 V.
- A host on the S3's own USB-C powers the controller only: that case is [TECH-POWER-VBUS-001](../../requirements/technical.md#tech-power-vbus-001), not this test.

## Results
| Date | Commit / build | VSYS on | VSYS off, battery | VSYS off, charger | Pass | By | Notes |
|---|---|---|---|---|---|---|---|
