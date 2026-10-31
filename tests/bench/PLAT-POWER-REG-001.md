# Bench test PLAT-POWER-REG-001 — TPS63020 module output and idle current

Requirement: [PLAT-POWER-REG-001](../../requirements/platform.md#plat-power-reg-001). Manual test, run at bring-up step **2 and 3.5** ([bring-up.md](bring-up.md)); add a line to *Results* every time it is run.

## Equipment
- A bench supply, 3.7 V, current limit 300 mA (stands in for the cells).
- A multimeter (V range, and mA / 10 A ranges for currents). With a µA range.

## Setup
1. TPS63020 module alone: EN tied to VIN, PS/SYNC bridged to GND, nothing on its output.
2. Its power LED removed first ([PLAT-POWER-SLEEP-001](PLAT-POWER-SLEEP-001.md)): with it, the < 0.1 mA criterion cannot pass.
3. Bench supply (+) through the meter to VIN, supply (−) to GND. Power up with the meter on its **A range** (the start-up current through a µA shunt can stall the converter), then switch to the µA range.

## Steps
1. Read the input current.
2. Meter on V: read VOUT / GND.

## Pass criteria
- VOUT 3.20–3.40 V (never 5 V).
- Input current < 0.1 mA. A few mA means it is stuck in PWM: check PS/SYNC.

## Results
| Date | Commit / build | VOUT | Idle current | Pass | By | Notes |
|---|---|---|---|---|---|---|
