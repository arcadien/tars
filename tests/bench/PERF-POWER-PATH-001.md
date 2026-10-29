# Bench test PERF-POWER-PATH-001 — power-path voltage drop

Requirement: [PERF-POWER-PATH-001](../../requirements/performance.md#perf-power-path-001). Manual test, run at bring-up steps **3.2** (drops) and **3.4** (charge current, cells in) ([bring-up.md](bring-up.md)); add a line to *Results* every time it is run.

## Equipment
- A bench supply, 3.7 V, current limit 300 mA (stands in for the cells).
- A multimeter (V range, and mA / 10 A ranges for currents).
- A 33 Ω ≥ 1 W resistor (≈ 110 mA on VSYS) with crocodile leads.
- A 5 V ≥ 2 A USB charger and a micro-USB cable.
- For step 3: one half-empty cell (3.6–3.8 V) in place of the bench supply.

## Setup
1. Power block on the bench, nothing on the 3V3. Bench supply on the TP4056 B+ / B− pads.
2. The 33 Ω load across VSYS and GND. VSYS and GND are reached at the X13 contacts of the power block (VSYS, GND amp).
3. SW1 on.

## Steps
1. On battery: read B+ and VSYS; drop = B+ − VSYS.
2. Plug the charger: read VUSB (TP4056 IN+ / IN− pads) and VSYS; drop = VUSB − VSYS.
3. Step 3.4, cells in: the half-empty cell alone (the other one unplugged), the meter in series in its B+ on the **10 A socket** (A socket on the board side, COM on the cell side: positive = into the cell), SW1 on, the 33 Ω load on VSYS. Plug the charger; after 1 min read the cell current.

## Pass criteria
- On battery: drop ≤ 0.10 V. A 0.5–0.7 V drop fails: Q1 runs on its body diode (R1 missing or wrong, or D1 leaking): fix it before going on.
- On the supply: drop ≤ 0.50 V.
- Step 3: cell current = the R_PROG value ± 10 % (0.45–0.55 A with 2.4 kΩ). Clearly more (~1 A) means Q1 is reversed: its body diode charges the cell from VUSB around the charger.

## Results
| Date | Commit / build | Drop on battery | Drop on supply | Cell current on mains | Pass | By | Notes |
|---|---|---|---|---|---|---|---|
