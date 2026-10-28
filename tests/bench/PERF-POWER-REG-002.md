# Bench test PERF-POWER-REG-002 — 3.3 V rail under Wi-Fi and audio load transients

Requirement: [PERF-POWER-REG-002](../../requirements/performance.md#perf-power-reg-002). Manual test, run at bring-up step **3.8** ([bring-up.md](bring-up.md)); add a line to *Results* every time it is run.

## Equipment
- The power block, the S3 Mini and the amplifier with its speaker wired.
- A bench supply set to **3.4 V**, current limit 2 A, in place of the cells.
- An oscilloscope (10× probe, short ground spring).
- A test firmware that transmits Wi-Fi continuously and plays a full-scale tone at the same time.

## Setup
1. Bench supply on the TP4056 B+ / B− pads. SW1 on.
2. Scope probe on the S3 Mini's 3V pin, ground on its GND pin; trigger on a falling edge at 3.15 V.

## Steps
1. Flash and start the test firmware (Wi-Fi TX + tone). Run it for 60 s; note the lowest 3V3 seen.
2. Check on the serial monitor that the controller did not reset.

## Pass criteria
- Lowest 3V3 ≥ 3.10 V, and no reset.

## Results
| Date | Commit / build | Lowest 3V3 | Reset | Pass | By | Notes |
|---|---|---|---|---|---|---|
