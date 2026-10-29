# Bench test PERF-POWER-REG-001 — 3.3 V rail static regulation

Requirement: [PERF-POWER-REG-001](../../requirements/performance.md#perf-power-reg-001). Manual test, run at bring-up step **3.5** ([bring-up.md](bring-up.md)); add a line to *Results* every time it is run.

## Equipment
- An adjustable bench supply, 3.0–5.0 V, current limit 1 A.
- A multimeter (V range, and mA / 10 A ranges for currents).
- A 33 Ω ≥ 1 W resistor (≈ 110 mA on VSYS) with crocodile leads.
- A 6.8 Ω ≥ 2 W resistor (≈ 500 mA).

## Setup
1. TPS63020 module alone: bench supply on VIN / GND (EN tied to VIN, PS/SYNC to GND), nothing else on its output.
2. Meter (V) on VOUT / GND, at the module's pads.

## Steps
1. No load: set the supply to 3.0, 3.4, 3.8, 4.2 and 5.0 V; note VOUT each time.
2. Same with the 33 Ω load on VOUT.
3. Same with the 6.8 Ω load on VOUT (the module warms up: 30 s per point).

## Pass criteria
- Every reading within 3.20–3.40 V (15 readings).

## Results
| Date | Commit / build | Lowest VOUT | Highest VOUT | Pass | By | Notes |
|---|---|---|---|---|---|---|
