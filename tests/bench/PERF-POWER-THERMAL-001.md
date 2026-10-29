# Bench test PERF-POWER-THERMAL-001 — leg wall temperature while charging (E-M8)

Requirement: [PERF-POWER-THERMAL-001](../../requirements/performance.md#perf-power-thermal-001). Manual test, run at bring-up step **3.9** ([bring-up.md](bring-up.md)); add a line to *Results* every time it is run.

## Equipment
- The assembled robot, lids closed, pack **partly discharged** (so it charges at full current for 30 min).
- A thermocouple or an IR thermometer.
- A 5 V ≥ 2 A USB charger and a micro-USB cable.
- A 4.7 Ω ≥ 10 W resistor (≈ 1 A on VSYS on mains, ~4.6 V) with crocodile leads.
- A room at 20–25 °C.

## Setup
1. Find the spot on the outer wall of the left leg right next to the TP4056; mark it with a pencil.

## Steps
1. Case A, robot off: plug the charger; read the wall temperature at 15 min and at 30 min.
2. Let it cool to room temperature, and discharge the pack a little again.
3. Case B, robot on with the 4.7 Ω load on VSYS (≈ 1 A on the external supply): plug the charger; read at 15 and 30 min.

## Pass criteria
- Every reading ≤ 45 °C. Above: R_PROG 3.6 kΩ ([PLAT-POWER-CHARGE-002](../../requirements/platform.md#plat-power-charge-002)) and run again.

## Results
| Date | Commit / build | A 15 / 30 min | B 15 / 30 min | Room | Pass | By | Notes |
|---|---|---|---|---|---|---|---|
