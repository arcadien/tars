# Bench test PERF-POWER-CHARGE-001 — full charge time

Requirement: [PERF-POWER-CHARGE-001](../../requirements/performance.md#perf-power-charge-001). Manual test, run at bring-up step **3.9** ([bring-up.md](bring-up.md)); add a line to *Results* every time it is run.

## Equipment
- The assembled robot.
- A multimeter (V range, and mA / 10 A ranges for currents).
- A 5 V ≥ 2 A USB charger and a micro-USB cable.
- A clock or a phone timer.

## Setup
1. Run the robot down to the 3.30 V cut-off, or discharge the pack through a 6.8 Ω ≥ 5 W resistor **on VSYS** (SW1 on, so the DW01 still protects the cells), until B+ reads 3.30 V under load.
2. Switch off, let the pack rest 30 min and note the rested B+ (a pack cut at 3.30 V under load recovers to ~3.4–3.5 V): that is the start of the timed charge. Note the R_PROG fitted (2.4 kΩ, or the 3.6 kΩ fallback).

## Steps
1. Plug the charger with the robot switched off; note the time.
2. Note the time when the TP4056 LED shows the end of charge.

## Pass criteria
- Duration ≤ 12 h with R_PROG 2.4 kΩ (0.5 A), ≤ 16 h with 3.6 kΩ (0.33 A).

## Results
| Date | Commit / build | R_PROG | B+ at start | Duration | Pass | By | Notes |
|---|---|---|---|---|---|---|---|
