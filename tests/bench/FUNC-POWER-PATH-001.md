# Bench test FUNC-POWER-PATH-001 — on the external supply, the system load does not draw from the battery

Requirement: [FUNC-POWER-PATH-001](../../requirements/functional.md#func-power-path-001). Manual test, run at bring-up step **3.4** ([bring-up.md](bring-up.md)); add a line to *Results* every time it is run.

## Equipment
- The power block with its cells, one of them **partly discharged** (3.6–3.9 V).
- A multimeter (V range, and mA / 10 A ranges for currents).
- A 33 Ω ≥ 1 W resistor (≈ 110 mA on VSYS) with crocodile leads.
- A 5 V ≥ 2 A USB charger and a micro-USB cable.

## Setup
1. Nothing on the 3V3 (TPS63020 output unloaded).
2. Unplug **X16** (right cell), so that the whole pack current goes through the meter, then **X12** (left cell). Join the two B− contacts of X12 with a short jumper. Put the meter on its **10 A socket** (the mA socket fuse blows at 0.5 A) in series in B+: **A socket on the board-side B+, COM on the cell-side B+**. A positive reading is current flowing **into** the cell (charge), a negative one current flowing out of it.
3. The 33 Ω load across VSYS and GND. VSYS and GND are reached at the X13 contacts of the power block (VSYS, GND amp).
4. SW1 on.

## Steps
1. Without the charger, read the cell current: about −110 mA (the load runs on the cell; this proves the wiring).
2. Plug the charger into the charge port. After 10 s, read the cell current; watch it for 5 min (min-hold if the meter has it) and note the lowest value.
3. Leave it plugged until the charge ends (TP4056 LED changes); note B+ and the last current.

## Pass criteria
- Step 2: the cell current never goes below −0.1 mA (no current out of the battery while on the supply).
- Step 3: the charge ends as [TECH-POWER-CHARGE-001](../../requirements/technical.md#tech-power-charge-001) requires (B+ 4.158–4.242 V, current ≤ 10 % of the set current, then off).

## Results
| Date | Commit / build | Step 1 current | Lowest current on USB | End of charge B+ / current | Pass | By | Notes |
|---|---|---|---|---|---|---|---|
