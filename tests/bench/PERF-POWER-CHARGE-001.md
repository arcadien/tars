# Bench test PERF-POWER-CHARGE-001 — full charge time

Requirement: [PERF-POWER-CHARGE-001](../../requirements/performance.md#perf-power-charge-001). Manual test, run at bring-up step **3.9** ([bring-up.md](bring-up.md)); add a line to *Results* every time it is run.

## Equipment
- The assembled robot.
- A multimeter (V range, and mA / 10 A ranges for currents).
- A 5 V ≥ 2 A USB charger and a micro-USB cable.
- A clock or a phone timer.

## Setup
1. Run the robot down to the 3.30 V cut-off (or discharge the pack through a 6.8 Ω resistor while watching B+).
2. Switch off, let the pack rest 30 min; check B+ ≈ 3.30 V. Note the R_PROG fitted (2.4 kΩ, or the 3.6 kΩ fallback).

## Steps
1. Plug the charger with the robot switched off; note the time.
2. Note the time when the TP4056 LED shows the end of charge.

## Pass criteria
- Duration ≤ 12 h with R_PROG 2.4 kΩ (0.5 A), ≤ 16 h with 3.6 kΩ (0.33 A).

## Results
| Date | Commit / build | R_PROG | B+ at start | Duration | Pass | By | Notes |
|---|---|---|---|---|---|---|---|
