# Bench test TECH-POWER-PROTECT-001 — pack protection opens on over-discharge and overcurrent

Requirement: [TECH-POWER-PROTECT-001](../../requirements/technical.md#tech-power-protect-001). Manual test, run at bring-up step **3.1** ([bring-up.md](bring-up.md)); add a line to *Results* every time it is run.

## Equipment
- An adjustable bench supply in place of the cells (current limit 300 mA for steps 1–2, 5 A for step 3).
- A multimeter (V range, and mA / 10 A ranges for currents).
- A 1 kΩ resistor, and a 1 Ω ≥ 5 W resistor (it only carries ~3.7 A for well under a second).

## Setup
1. Bench supply on the TP4056 B+ / B− pads, set to 3.7 V.
2. The 1 kΩ resistor across OUT+ / OUT−; meter (V) across it.

## Steps
1. Check OUT ≈ B+ (the protection conducts).
2. Lower the supply in 0.05 V steps (slowly below 2.7 V), waiting 2 s per step, until OUT drops to 0 V. Note the supply voltage.
3. Back to 3.7 V, current limit 5 A. Swap the 1 kΩ for the 1 Ω resistor across OUT+ / OUT− (≈ 3.7 A), meter (V) still across it: note whether OUT drops to 0 V and within how long (count, or a scope on OUT). Disconnect the load at once; the protection recovers once the load is removed (or after briefly connecting a charger).

## Pass criteria
- Step 2: OUT opens between 2.3 and 2.5 V.
- Step 3: OUT opens within 1 s with the 1 Ω load (overcurrent).

## Results
| Date | Commit / build | Cut-off voltage | Overcurrent cut (time) | Pass | By | Notes |
|---|---|---|---|---|---|---|
