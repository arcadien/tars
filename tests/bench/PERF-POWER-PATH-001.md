# Bench test PERF-POWER-PATH-001 — power-path voltage drop

Requirement: [PERF-POWER-PATH-001](../../requirements/performance.md#perf-power-path-001). Manual test, run at bring-up step **3.2** ([bring-up.md](bring-up.md)); add a line to *Results* every time it is run.

## Equipment
- A bench supply, 3.7 V, current limit 300 mA (stands in for the cells).
- A multimeter (V range, and mA / 10 A ranges for currents).
- A 33 Ω ≥ 1 W resistor (≈ 110 mA on VSYS) with crocodile leads.
- A 5 V ≥ 2 A USB charger and a micro-USB cable.

## Setup
1. Power block on the bench, nothing on the 3V3. Bench supply on the TP4056 B+ / B− pads.
2. The 33 Ω load across VSYS and GND. VSYS and GND are reached at the X13 contacts of the power block (VSYS, GND amp).
3. SW1 on.

## Steps
1. On battery: read B+ and VSYS; drop = B+ − VSYS.
2. Plug the charger: read VUSB (TP4056 IN+ / IN− pads) and VSYS; drop = VUSB − VSYS.

## Pass criteria
- On battery: drop ≤ 0.10 V. A 0.5–0.7 V drop fails: Q1 runs on its body diode (R1 missing or wrong, or D1 leaking): fix it before going on.
- On the supply: drop ≤ 0.50 V.

## Results
| Date | Commit / build | Drop on battery | Drop on supply | Pass | By | Notes |
|---|---|---|---|---|---|---|
