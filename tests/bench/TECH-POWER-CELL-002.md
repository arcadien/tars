# Bench test TECH-POWER-CELL-002 — cells matched before they go in parallel

Requirement: [TECH-POWER-CELL-002](../../requirements/technical.md#tech-power-cell-002). Manual test, run at bring-up step **2** ([bring-up.md](bring-up.md)); add a line to *Results* every time it is run.

## Equipment
- Both 18650 cells (same model and age).
- A single-cell charger (or the TP4056 module).
- A multimeter (V range, and mA / 10 A ranges for currents).

## Setup
1. Check both labels: same model, same batch or purchase date.

## Steps
1. Charge each cell on its own to full.
2. Let both rest 1 h.
3. Read each cell voltage, just before the first insertion in the robot.

## Pass criteria
- Same model and age.
- The two voltages differ by ≤ 0.05 V.

## Results
| Date | Commit / build | Model / date | Left V | Right V | Pass | By | Notes |
|---|---|---|---|---|---|---|---|
