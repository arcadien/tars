# Bench test TECH-POWER-CHARGE-001 — CC/CV charge ending at 4.20 V

Requirement: [TECH-POWER-CHARGE-001](../../requirements/technical.md#tech-power-charge-001). Manual test, run at bring-up step **3.1** ([bring-up.md](bring-up.md)); add a line to *Results* every time it is run.

## Equipment
- The TP4056 module (USB in on its own micro-USB at this step).
- One half-empty cell (3.6–3.8 V).
- A multimeter (V range, and mA / 10 A ranges for currents).

## Setup
1. Cell on B+ / B−, the meter (current range) in series in B+: A socket on the module's B+, COM on the cell +.

## Steps
1. USB in. Note the current (constant-current phase, ≈ the set current).
2. Check every 30 min: the current stays level, then falls (constant-voltage phase).
3. When the LED shows the end of charge: read the current, then B+ at the cell terminals (meter on V).

## Pass criteria
- Final B+ 4.158–4.242 V.
- The current falls to ≤ 10 % of the set current, then stops.

## Results
| Date | Commit / build | CC current | Final B+ | Last current | Pass | By | Notes |
|---|---|---|---|---|---|---|---|
