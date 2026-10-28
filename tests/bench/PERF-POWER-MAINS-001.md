# Bench test PERF-POWER-MAINS-001 — supply voltage under the maximum combined load

Requirement: [PERF-POWER-MAINS-001](../../requirements/performance.md#perf-power-mains-001). Manual test, run at bring-up step **3.9** ([bring-up.md](bring-up.md)); add a line to *Results* every time it is run.

## Equipment
- The assembled robot, pack **half empty** (charging at full current for 30 min).
- A 5 V ≥ 2 A USB charger and a micro-USB cable.
- A 3.9 Ω 5 W resistor (≈ 1 A on VSYS) with crocodile leads.
- A multimeter (V range, and mA / 10 A ranges for currents).

## Setup
1. Meter (V) on the TP4056 IN+ / IN− pads.
2. SW1 on, the 3.9 Ω load on VSYS (1 A).

## Steps
1. Plug the charger. Read the voltage every 5 min for 30 min (7 readings).

## Pass criteria
- Every reading ≥ 4.60 V.

## Results
| Date | Commit / build | Lowest VUSB | Charger used | Pass | By | Notes |
|---|---|---|---|---|---|---|
