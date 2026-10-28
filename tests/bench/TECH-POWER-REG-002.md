# Bench test TECH-POWER-REG-002 — no reverse current into the regulator when the S3 LDO also drives 3V3

Requirement: [TECH-POWER-REG-002](../../requirements/technical.md#tech-power-reg-002). Manual test, run at bring-up step **3.7** ([bring-up.md](bring-up.md)); add a line to *Results* every time it is run.

## Equipment
- The power block, the S3 Mini on the 3V3, cells or the bench supply at 3.7 V.
- A multimeter (V range, and mA / 10 A ranges for currents).
- A PC (host) and a USB-C cable.

## Setup
1. SW1 on, on battery. The meter (mA range) in series in the TPS63020 VIN wire: A socket on the VSYS side, COM on the module's VIN (a positive reading flows into the module).

## Steps
1. Controller idle: note the TPS63020 input current.
2. Plug the S3 Mini's USB-C into the PC (switched on); after 10 s, note the input current again.
3. Read the 3V3 at the S3's 3V pin.

## Pass criteria
- Step 2: input current ≥ 0 (never negative).
- Step 3: 3V3 within 3.20–3.40 V ([PERF-POWER-REG-001](../../requirements/performance.md#perf-power-reg-001)).

## Results
| Date | Commit / build | Current, host off | Current, host on | 3V3 | Pass | By | Notes |
|---|---|---|---|---|---|---|---|
