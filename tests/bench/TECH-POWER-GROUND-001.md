# Bench test TECH-POWER-GROUND-001 — every power return within 0.1 Ω of the star point

Requirement: [TECH-POWER-GROUND-001](../../requirements/technical.md#tech-power-ground-001). Manual test, run at bring-up step **3.4 (cells in)** ([bring-up.md](bring-up.md)); add a line to *Results* every time it is run. The schematic part (no load ground on B−) is checked by `tests/test_power.py`.

An ohmmeter cannot read 0.1 Ω on a live circuit (and its leads alone are 0.1–0.2 Ω): the resistance is measured as a voltage drop at a known current. 100 mV at 1 A = 0.1 Ω.

## Equipment
- The power block with its cells (charged, ≥ 3.8 V), the protection switched on (OUT+ ≈ B+).
- A multimeter on its mV range, two thin probe tips.
- A 3.9 Ω ≥ 10 W resistor (≈ 1 A on battery) with crocodile leads.
- The star point: the GND bus on row 1 of the power-path board.

## Setup
1. SW1 on, nothing on the 3V3 except the TPS63020 unloaded.
2. The 3.9 Ω load from VSYS to the **amplifier GND** wire end (X13 "GND amp" contact), so the 1 A returns through that wire and the star.

## Steps
1. Black probe on the star bus (row 1). Red probe on the amplifier GND at the load end: read the mV.
2. Move the load return to the TPS63020 GND pad; red probe on that pad: read the mV.
3. Load return back on the star; red probe on the TP4056 OUT− pad, then on B− (the cells' negative): read the mV each.

## Pass criteria
- Every reading < 100 mV at ≈ 1 A (< 0.1 Ω from the star point).
- B− reads a few tens of mV at most (the DW01 switches between B− and OUT−): more means the protection is not fully on.

## Results
| Date | Commit / build | Amp GND | TPS GND | OUT− | B− | Load current | Pass | By | Notes |
|---|---|---|---|---|---|---|---|---|---|
