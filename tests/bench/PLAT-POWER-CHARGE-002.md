# Bench test PLAT-POWER-CHARGE-002 — charge current set by R_PROG 2.4 kΩ

Requirement: [PLAT-POWER-CHARGE-002](../../requirements/platform.md#plat-power-charge-002). Manual test, run at bring-up step **2 and 3.1** ([bring-up.md](bring-up.md)); add a line to *Results* every time it is run.

## Equipment
- The TP4056 module, unpowered.
- A multimeter (V range, and mA / 10 A ranges for currents).
- One half-empty cell (3.6–3.8 V).
- A 5 V ≥ 2 A USB charger and a micro-USB cable.
- A thermometer (IR or thermocouple).

## Setup
1. Module unpowered: measure R_PROG in place (marking "242", or "362" for the fallback).
2. Cell on B+ / B−, the meter on its **10 A socket** (the mA socket fuse blows at 0.5 A) in series in B+: A socket on the module's B+, COM on the cell +.

## Steps
1. Note R_PROG.
2. USB into the module; after 1 min, read the charge current.
3. Module in open air: after 15 min, read the temperature of the TP4056 chip.

## Pass criteria
- R_PROG within ± 5 %: 2.28–2.52 kΩ (fallback 3.42–3.78 kΩ).
- Charge current 0.45–0.55 A (fallback 0.30–0.36 A).
- Chip < 60 °C.

## Results
| Date | Commit / build | R_PROG | Current | Chip °C | Pass | By | Notes |
|---|---|---|---|---|---|---|---|
