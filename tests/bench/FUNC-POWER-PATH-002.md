# Bench test FUNC-POWER-PATH-002 — plugging or unplugging the supply does not drop the system rail

Requirement: [FUNC-POWER-PATH-002](../../requirements/functional.md#func-power-path-002). Manual test, run at bring-up step **3.4** ([bring-up.md](bring-up.md)); add a line to *Results* every time it is run.

Part (b) of the acceptance (boot counter and reset reason over the same cycles) is an on-target firmware test: it comes with the firmware.

## Equipment
- Both cells, charged (≥ 3.9 V).
- A multimeter (V range, and mA / 10 A ranges for currents). With min-hold, or a scope.
- A 33 Ω ≥ 1 W resistor (≈ 110 mA on VSYS) with crocodile leads.
- A 3.9 Ω 5 W resistor (≈ 1 A on VSYS) with crocodile leads.
- A 5 V ≥ 2 A USB charger and a micro-USB cable.

## Setup
1. SW1 on, nothing on the 3V3.
2. Meter (V, min-hold) or scope across VSYS and GND. VSYS and GND are reached at the X13 contacts of the power block (VSYS, GND amp).
3. The 33 Ω load across VSYS and GND.

## Steps
1. Reset the min-hold. Plug and unplug the charger 20 times (about 2 s in, 2 s out). Note the minimum VSYS.
2. Swap the load for the 3.9 Ω 5 W resistor (it gets hot: keep it off the table). Repeat the 20 cycles; note the minimum VSYS.

## Pass criteria
- Both minima ≥ 3.0 V.

## Results
| Date | Commit / build | Min VSYS at 110 mA | Min VSYS at 1 A | Pass | By | Notes |
|---|---|---|---|---|---|---|
