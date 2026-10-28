# Bench test TECH-POWER-PROTECT-001 — pack protection opens on over-discharge

Requirement: [TECH-POWER-PROTECT-001](../../requirements/technical.md#tech-power-protect-001). Manual test, run at bring-up step **3.1** ([bring-up.md](bring-up.md)); add a line to *Results* every time it is run.

## Equipment
- An adjustable bench supply in place of the cells (current limit 300 mA).
- A multimeter (V range, and mA / 10 A ranges for currents).
- A 1 kΩ resistor.

## Setup
1. Bench supply on the TP4056 B+ / B− pads, set to 3.7 V.
2. The 1 kΩ resistor across OUT+ / OUT−; meter (V) across it.

## Steps
1. Check OUT ≈ B+ (the protection conducts).
2. Lower the supply in 0.05 V steps (slowly below 2.7 V), waiting 2 s per step, until OUT drops to 0 V. Note the supply voltage.

## Pass criteria
- OUT opens between 2.3 and 2.5 V.

## Results
| Date | Commit / build | Cut-off voltage | Pass | By | Notes |
|---|---|---|---|---|---|
