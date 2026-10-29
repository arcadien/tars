# Bench test PLAT-POWER-FUSE-001 — polyfuses F1 / F2 at each cell's + plate

Requirement: [PLAT-POWER-FUSE-001](../../requirements/platform.md#plat-power-fuse-001). Manual test, run at bring-up step **3.4** ([bring-up.md](bring-up.md)); add a line to *Results* every time it is run.

## Equipment
- A multimeter (V range, and mA / 10 A ranges for currents). With a low-ohm range (or a 4-wire meter).
- Both cells.
- A 3.9 Ω ≥ 10 W resistor (≈ 1 A on battery) with crocodile leads.

## Setup
1. Cells out. Short the meter leads and note their resistance (to subtract).

## Steps
1. Read F1 and F2 cold, each across its two legs; subtract the lead resistance.
2. Cells in, SW1 on, the 3.9 Ω load on VSYS (≈ 1 A from the pack). Read the voltage across F1, then across F2.
3. Read each branch voltage: cell side of F1 to B−, cell side of F2 to B−.

## Pass criteria
- Each fuse < 0.2 Ω cold.
- Drop across each fuse < 0.15 V at the 1 A load.
- Both branches within 0.02 V of each other.

## Results
| Date | Commit / build | F1 / F2 Ω | F1 / F2 drop | Branch V | Pass | By | Notes |
|---|---|---|---|---|---|---|---|
